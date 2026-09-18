import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';

export type Theme = 'system' | 'light' | 'dark' | 'aura' | 'nordic' | 'onyx';

export interface ThemeContextValue {
  theme: Theme;
  effectiveTheme: 'light' | 'dark' | 'aura' | 'nordic' | 'onyx';
  setTheme: (theme: Theme) => void;
}

const Context = createContext<ThemeContextValue>({
  theme: 'system',
  effectiveTheme: 'light',
  setTheme: () => undefined,
});

const VALID_THEMES: Theme[] = ['system', 'light', 'dark', 'aura', 'nordic', 'onyx'];

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<Theme>(() => {
    const value = localStorage.getItem('evalforge_theme') as Theme;
    return VALID_THEMES.includes(value) ? value : 'system';
  });

  const [effectiveTheme, setEffectiveTheme] = useState<'light' | 'dark' | 'aura' | 'nordic' | 'onyx'>(() => {
    if (theme === 'system') {
      return typeof window !== 'undefined' && window.matchMedia('(prefers-color-scheme: dark)').matches
        ? 'dark'
        : 'light';
    }
    return theme;
  });

  useEffect(() => {
    const media = matchMedia('(prefers-color-scheme: dark)');
    const apply = () => {
      const active: 'light' | 'dark' | 'aura' | 'nordic' | 'onyx' =
        theme === 'system' ? (media.matches ? 'dark' : 'light') : theme;

      setEffectiveTheme(active);
      document.documentElement.dataset.theme = active;

      const isDark = active === 'dark' || active === 'onyx';
      if (isDark) {
        document.documentElement.classList.add('dark');
        document.documentElement.dataset.colorMode = 'dark';
      } else {
        document.documentElement.classList.remove('dark');
        document.documentElement.dataset.colorMode = 'light';
      }
    };

    apply();
    try {
      localStorage.setItem('evalforge_theme', theme);
    } catch {
      // Storage access fail-safe
    }

    media.addEventListener('change', apply);
    return () => media.removeEventListener('change', apply);
  }, [theme]);

  return (
    <Context.Provider value={{ theme, effectiveTheme, setTheme }}>
      {children}
    </Context.Provider>
  );
}

export const useTheme = () => useContext(Context);
