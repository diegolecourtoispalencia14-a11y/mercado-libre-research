import { scoreColor, scoreLabel } from '../utils/scoring'

export default function ScoreBadge({ score, trendAvailable }) {
  return (
    <div className="flex flex-col items-center gap-1">
      <span className={`text-2xl font-bold ${scoreColor(score)}`}>{score}</span>
      <span className="text-xs text-gray-500">{scoreLabel(score)}</span>
      {!trendAvailable && (
        <span className="text-xs bg-yellow-100 text-yellow-700 px-2 py-0.5 rounded">
          sin datos de tendencia
        </span>
      )}
    </div>
  )
}
