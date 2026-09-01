import React, { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react';
import type { ReactNode } from 'react';
import { api } from '../services/api';
import type { Project } from '../services/api';

interface WorkspaceContextType {
  projects: Project[];
  currentProjectId: string | null;
  currentProject: Project | null;
  isLoading: boolean;
  error: string | null;
  setCurrentProjectId: (id: string) => void;
  refreshProjects: () => Promise<void>;
  clearError: () => void;
}

const WorkspaceContext = createContext<WorkspaceContextType | undefined>(undefined);

const ACTIVE_PROJECT_KEY = 'evalforge_active_project_id';

export const WorkspaceProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [currentProjectId, setCurrentProjectIdState] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Sequence ref to ignore stale async responses from rapid project switches / requests
  const fetchSeqRef = useRef(0);

  const fetchProjects = useCallback(async () => {
    const currentSeq = ++fetchSeqRef.current;
    setIsLoading(true);
    setError(null);

    try {
      const list = await api.projects.list();
      // Ignore if a newer fetch request was initiated in the meantime
      if (currentSeq !== fetchSeqRef.current) return;

      const availableList: Project[] = Array.isArray(list) ? list : list?.data || [];
      setProjects(availableList);

      const storedId = localStorage.getItem(ACTIVE_PROJECT_KEY);
      // Validate stored project ID against the user's available project list
      if (storedId && availableList.some((p) => p.id === storedId)) {
        setCurrentProjectIdState(storedId);
      } else if (availableList.length > 0) {
        // Default to first authoritative project if stored ID is invalid or unauthorized
        setCurrentProjectIdState(availableList[0].id);
        localStorage.setItem(ACTIVE_PROJECT_KEY, availableList[0].id);
      } else {
        setCurrentProjectIdState(null);
        localStorage.removeItem(ACTIVE_PROJECT_KEY);
      }
    } catch (err) {
      if (currentSeq !== fetchSeqRef.current) return;
      console.error('Failed to fetch workspace projects:', err);
      setError('Unable to synchronize workspace projects from server');
      // On failure, preserve existing state if valid, or fallback gracefully
      setProjects((prev) => prev);
    } finally {
      if (currentSeq === fetchSeqRef.current) {
        setIsLoading(false);
      }
    }
  }, []);

  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  const setCurrentProjectId = (id: string) => {
    if (!id) return;
    // Only accept setting project ID if it belongs to available project list or initialization is pending
    if (projects.length === 0 || projects.some((p) => p.id === id)) {
      setCurrentProjectIdState(id);
      localStorage.setItem(ACTIVE_PROJECT_KEY, id);
    } else {
      console.warn(`Attempted to select unauthorized or non-existent project ID: ${id}`);
    }
  };

  const clearError = () => setError(null);

  const currentProject = projects.find((p) => p.id === currentProjectId) || null;

  return (
    <WorkspaceContext.Provider
      value={{
        projects,
        currentProjectId,
        currentProject,
        isLoading,
        error,
        setCurrentProjectId,
        refreshProjects: fetchProjects,
        clearError,
      }}
    >
      {children}
    </WorkspaceContext.Provider>
  );
};

export const useWorkspace = (): WorkspaceContextType => {
  const context = useContext(WorkspaceContext);
  if (!context) {
    throw new Error('useWorkspace must be used within a WorkspaceProvider');
  }
  return context;
};
