import { scoreColor, scoreLabel } from '../utils/scoring'

export default function ScoreBadge({ score, trendAvailable }) {
  return (
    <div className="flex flex-col items-center justify-center p-2 rounded-xl bg-white/[0.03] border border-white/[0.06] min-w-[90px]">
      <span className={`text-2xl font-extrabold font-mono tracking-tight ${scoreColor(score)}`}>
        {score}
      </span>
      <span className="text-[11px] font-medium text-gray-400 mt-0.5 whitespace-nowrap">
        {scoreLabel(score)}
      </span>
      {!trendAvailable && (
        <span className="text-[10px] font-mono bg-yellow-500/10 text-yellow-400 border border-yellow-500/20 px-2 py-0.5 rounded-full mt-1">
          sin datos de tendencia
        </span>
      )}
    </div>
  )
}

