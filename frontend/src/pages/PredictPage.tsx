import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Target, TrendingUp, BarChart3, AlertCircle } from 'lucide-react';
import { api, type Player, type MatchPrediction } from '../lib/api';


const PredictPage: React.FC = () => {
  const [player1, setPlayer1] = useState('');
  const [player2, setPlayer2] = useState('');
  const [surface, setSurface] = useState<'hard' | 'clay' | 'grass'>('hard');
  const [isPredicting, setIsPredicting] = useState(false);
  const [prediction, setPrediction] = useState<MatchPrediction | null>(null);

  const { data: players } = useQuery({
    queryKey: ['players', 'all'],
    queryFn: () => api.getPlayers({ limit: 1000, active: true }),
  });

  const handlePrediction = async () => {
    if (!player1 || !player2 || player1 === player2) {
      alert('Please select two different players');
      return;
    }

    setIsPredicting(true);
    try {
      const result = await api.predictMatch(player1, player2, surface);
      setPrediction(result);
    } catch (error) {
      console.error('Prediction error:', error);
      alert('Error making prediction. Please try again.');
    } finally {
      setIsPredicting(false);
    }
  };

  const getConfidenceColor = (confidence: string) => {
    switch (confidence.toLowerCase()) {
      case 'high': return 'text-green-400';
      case 'medium': return 'text-yellow-400';
      case 'low': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  const getSurfaceIcon = (surface: string) => {
    switch (surface) {
      case 'clay': return '🟤';
      case 'grass': return '🟢';
      default: return '🔵';
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2 flex items-center gap-3">
            <Target className="text-primary-500" />
            Match Prediction
          </h1>
          <p className="text-gray-400">
            Predict match outcomes using ELO ratings, surface performance, and current form
          </p>
        </div>

        {/* Prediction Form */}
        <div className="bg-gray-800 rounded-lg p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Player 1 */}
            <div>
              <label className="block text-sm text-gray-300 mb-2">Player 1</label>
              <select
                value={player1}
                onChange={(e) => setPlayer1(e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-primary-500"
              >
                <option value="">Select Player 1</option>
                {players?.map((player: Player) => (
                  <option key={player.name} value={player.name}>
                    {player.name} ({Math.round(player.elo)} ELO)
                  </option>
                ))}
              </select>
            </div>

            {/* Player 2 */}
            <div>
              <label className="block text-sm text-gray-300 mb-2">Player 2</label>
              <select
                value={player2}
                onChange={(e) => setPlayer2(e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-primary-500"
              >
                <option value="">Select Player 2</option>
                {players?.map((player: Player) => (
                  <option key={player.name} value={player.name}>
                    {player.name} ({Math.round(player.elo)} ELO)
                  </option>
                ))}
              </select>
            </div>

            {/* Surface */}
            <div>
              <label className="block text-sm text-gray-300 mb-2">Surface</label>
              <select
                value={surface}
                onChange={(e) => setSurface(e.target.value as 'hard' | 'clay' | 'grass')}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-primary-500"
              >
                <option value="hard">Hard Court 🔵</option>
                <option value="clay">Clay Court 🟤</option>
                <option value="grass">Grass Court 🟢</option>
              </select>
            </div>

            {/* Predict Button */}
            <div className="flex items-end">
              <button
                onClick={handlePrediction}
                disabled={isPredicting || !player1 || !player2}
                className="w-full px-6 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isPredicting ? 'Predicting...' : 'Predict Match'}
              </button>
            </div>
          </div>
        </div>

        {/* Prediction Results */}
        {prediction && (
          <div className="space-y-6">
            {/* Main Prediction */}
            <div className="bg-gray-800 rounded-lg p-6">
              <div className="flex items-center gap-3 mb-4">
                <BarChart3 className="text-primary-500 w-6 h-6" />
                <h2 className="text-2xl font-bold">Prediction Result</h2>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="text-center">
                  <div className="text-4xl font-bold text-primary-500 mb-2">
                    {prediction.prediction.winner}
                  </div>
                  <div className="text-gray-400 mb-4">Predicted Winner</div>
                  <div className="text-3xl font-bold text-green-400">
                    {(prediction.prediction.probability * 100).toFixed(1)}%
                  </div>
                  <div className="text-sm text-gray-400">Win Probability</div>
                </div>
                
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-400">Surface:</span>
                    <span className="text-white">
                      {getSurfaceIcon(prediction.surface)} {prediction.surface.charAt(0).toUpperCase() + prediction.surface.slice(1)}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-400">Confidence:</span>
                    <span className={`font-semibold ${getConfidenceColor(prediction.prediction.confidence)}`}>
                      {prediction.prediction.confidence}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-400">Match:</span>
                    <span className="text-white">
                      {prediction.player1} vs {prediction.player2}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Factors Breakdown */}
            <div className="bg-gray-800 rounded-lg p-6">
              <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                <TrendingUp className="text-primary-500 w-5 h-5" />
                Prediction Factors
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">ELO Difference:</span>
                    <span className={`font-semibold ${prediction.factors.elo_difference > 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {prediction.factors.elo_difference > 0 ? '+' : ''}{prediction.factors.elo_difference.toFixed(0)}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Surface Advantage:</span>
                    <span className={`font-semibold ${prediction.factors.surface_advantage > 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {prediction.factors.surface_advantage > 0 ? '+' : ''}{prediction.factors.surface_advantage.toFixed(1)}%
                    </span>
                  </div>
                </div>
                
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Form Advantage:</span>
                    <span className={`font-semibold ${prediction.factors.form_advantage > 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {prediction.factors.form_advantage > 0 ? '+' : ''}{prediction.factors.form_advantage.toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Big Match Experience:</span>
                    <span className={`font-semibold ${prediction.factors.big_match_experience > 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {prediction.factors.big_match_experience > 0 ? '+' : ''}{prediction.factors.big_match_experience.toFixed(1)}%
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Detailed Breakdown */}
            <div className="bg-gray-800 rounded-lg p-6">
              <h3 className="text-xl font-bold mb-4">Calculation Breakdown</h3>
              
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-gray-400">Base Probability:</span>
                  <span className="text-white">{prediction.breakdown.base_probability.toFixed(1)}%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-400">Surface Adjusted:</span>
                  <span className="text-white">{prediction.breakdown.surface_adjusted.toFixed(1)}%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-400">Form Adjusted:</span>
                  <span className="text-white">{prediction.breakdown.form_adjusted.toFixed(1)}%</span>
                </div>
                {prediction.breakdown.clamped && (
                  <div className="flex items-center gap-2 text-yellow-400">
                    <AlertCircle className="w-4 h-4" />
                    <span className="text-sm">Probability clamped to 5-95% range</span>
                  </div>
                )}
              </div>
            </div>

            {/* Note */}
            <div className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <AlertCircle className="text-blue-400 w-5 h-5 mt-0.5" />
                <div>
                  <h4 className="font-semibold text-blue-400 mb-1">Note</h4>
                  <p className="text-blue-200 text-sm">{prediction.note}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Instructions */}
        {!prediction && (
          <div className="bg-gray-800 rounded-lg p-6">
            <h3 className="text-xl font-bold mb-4">How It Works</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-semibold text-primary-500 mb-2">Rating Systems</h4>
                <ul className="text-sm text-gray-400 space-y-1">
                  <li>• ELO: Base skill level comparison</li>
                  <li>• Surface Performance: Recent surface-specific results</li>
                  <li>• Form Index: Last 20 matches with opponent quality</li>
                  <li>• Big Match Rating: Performance vs elite opponents</li>
                </ul>
              </div>
              <div>
                <h4 className="font-semibold text-primary-500 mb-2">Prediction Factors</h4>
                <ul className="text-sm text-gray-400 space-y-1">
                  <li>• ELO difference provides base probability</li>
                  <li>• Surface advantage adjusts for court type</li>
                  <li>• Form advantage considers recent performance</li>
                  <li>• Probabilities clamped to 5-95% for realism</li>
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PredictPage;