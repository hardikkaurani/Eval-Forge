import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import type { ReactNode } from 'react';
import { api } from '../services/api';
import type { Project } from '../services/api';

interface WorkspaceContextType {
  projects: Project[];
  currentProjectId: string | null;
  currentProject: Project | null;
  isLoading: boolean;
  setCurrentProjectId: (id: string) => void;
  refreshProjects: () => Promise<void>;
}

const WorkspaceContext = createContext<WorkspaceContextType | undefined>(undefined);

const ACTIVE_PROJECT_KEY = 'evalforge_active_project_id';

export const WorkspaceProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [currentProjectId, setCurrentProjectIdState] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const fetchProjects = useCallback(async () => {
    setIsLoading(true);
    try {
      const list = await api.projects.list();
      setProjects(list || []);
      
      const storedId = localStorage.getItem(ACTIVE_PROJECT_KEY);
      if (storedId && list.some((p: Project) => p.id === storedId)) {
        setCurrentProjectIdState(storedId);
      } else if (list.length > 0) {
        setCurrentProjectIdState(list[0].id);
        localStorage.setItem(ACTIVE_PROJECT_KEY, list[0].id);
      }
    } catch (err) {
      console.error('Failed to fetch workspace projects:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  const setCurrentProjectId = (id: string) => {
    setCurrentProjectIdState(id);
    localStorage.setItem(ACTIVE_PROJECT_KEY, id);
  };

  const currentProject = projects.find((p) => p.id === currentProjectId) || null;

  return (
    <WorkspaceContext.Provider
      value={{
        projects,
        currentProjectId,
        currentProject,
        isLoading,
        setCurrentProjectId,
        refreshProjects: fetchProjects,
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
