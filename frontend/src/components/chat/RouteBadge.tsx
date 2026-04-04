import type { RouteInfo } from '@/types/api'

const ROUTE_COLORS: Record<string, string> = {
  A: 'bg-sky-100 text-sky-700 dark:bg-sky-900/30 dark:text-sky-300',
  B: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300',
  C: 'bg-violet-100 text-violet-700 dark:bg-violet-900/30 dark:text-violet-300',
  D: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300',
  E: 'bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-300',
}

export default function RouteBadge({ route }: { route: RouteInfo }) {
  const colorClass = ROUTE_COLORS[route.route] || ROUTE_COLORS.A

  return (
    <div className="flex items-center gap-1.5 mb-1.5">
      <span className={`text-[9px] px-2 py-0.5 rounded-md font-semibold ${colorClass}`}>
        Route {route.route}
      </span>
      <span className="text-[10px]" style={{ color: 'var(--text-muted)' }}>
        {route.route_name}
      </span>
    </div>
  )
}
