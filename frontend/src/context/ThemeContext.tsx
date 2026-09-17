import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';
type Theme = 'system' | 'light' | 'dark';
const Context = createContext<{ theme: Theme; setTheme: (theme: Theme) => void }>({
  theme: 'system',
  setTheme: () => undefined,
});
export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<Theme>(() => {
    const value = localStorage.getItem('evalforge_theme');
    return value === 'dark' || value === 'light' ? value : 'system';
  });
  useEffect(() => {
    const media = matchMedia('(prefers-color-scheme: dark)');
    const apply = () => {
      document.documentElement.dataset.theme =
        theme === 'system' ? (media.matches ? 'dark' : 'light') : theme;
    };
    apply();
    localStorage.setItem('evalforge_theme', theme);
    media.addEventListener('change', apply);
    return () => media.removeEventListener('change', apply);
  }, [theme]);
  return <Context.Provider value={{ theme, setTheme }}>{children}</Context.Provider>;
}
export const useTheme = () => useContext(Context);
