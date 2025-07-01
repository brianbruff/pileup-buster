import { useTheme } from '../contexts/ThemeContext'

export default function ThemeToggle() {
  const { theme, setTheme, resolvedTheme } = useTheme()

  const cycleTheme = () => {
    if (theme === 'light') {
      setTheme('dark')
    } else if (theme === 'dark') {
      setTheme('auto')
    } else {
      setTheme('light')
    }
  }

  const getThemeIcon = () => {
    if (theme === 'auto') {
      return resolvedTheme === 'dark' ? '🌙' : '☀️'
    }
    return theme === 'dark' ? '🌙' : '☀️'
  }

  const getThemeLabel = () => {
    if (theme === 'auto') {
      return `Auto (${resolvedTheme})`
    }
    return theme === 'dark' ? 'Dark' : 'Light'
  }

  return (
    <button
      onClick={cycleTheme}
      className="theme-toggle"
      title={`Current theme: ${getThemeLabel()}. Click to cycle themes.`}
      type="button"
      aria-label={`Switch theme. Current: ${getThemeLabel()}`}
    >
      <span className="theme-icon">{getThemeIcon()}</span>
      <span className="theme-label">{getThemeLabel()}</span>
    </button>
  )
}