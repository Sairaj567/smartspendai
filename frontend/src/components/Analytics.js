import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  TrendingUp, 
  TrendingDown, 
  PieChart, 
  BarChart3, 
  Calendar,
  Brain,
  Menu,
  LogOut,
  Home,
  Receipt,
  CreditCard,
  Filter,
  ArrowUpRight
} from 'lucide-react';
import { Link } from 'react-router-dom';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Analytics = ({ user, onLogout }) => {
  const [summary, setSummary] = useState(null);
  const [trends, setTrends] = useState(null);
  const [loading, setLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [selectedPeriod, setSelectedPeriod] = useState(30);

  useEffect(() => {
    loadAnalytics();
  }, [user, selectedPeriod]);

  const loadAnalytics = async () => {
    try {
      const [summaryRes, trendsRes] = await Promise.all([
        axios.get(`${API}/analytics/spending-summary/${user.id}`),
        axios.get(`${API}/analytics/spending-trends/${user.id}?days=${selectedPeriod}`)
      ]);
      
      setSummary(summaryRes.data);
      setTrends(trendsRes.data);
    } catch (error) {
      console.error('Error loading analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const sidebarItems = [
    { icon: Home, label: 'Dashboard', path: '/dashboard' },
    { icon: BarChart3, label: 'Analytics', path: '/analytics', active: true },
    { icon: Receipt, label: 'Transactions', path: '/transactions' },
    { icon: Brain, label: 'AI Insights', path: '/insights' },
    { icon: CreditCard, label: 'Pay', path: '/pay' }
  ];

  const getCategoryIcon = (category) => {
    const icons = {
      'Food & Dining': '🍴',
      'Transportation': '🚗',
      'Shopping': '🛍️',
      'Entertainment': '🎨',
      'Bills & Utilities': '📝',
      'Healthcare': '🏥',
      'Education': '📚',
      'Income': '💰',
      'Investments': '📈'
    };
    return icons[category] || '💳';
  };

  const getCategoryColor = (index) => {
    const colors = [
      'from-blue-500 to-blue-600',
      'from-indigo-500 to-indigo-600', 
      'from-purple-500 to-purple-600',
      'from-pink-500 to-pink-600',
      'from-red-500 to-red-600',
      'from-orange-500 to-orange-600',
      'from-yellow-500 to-yellow-600',
      'from-green-500 to-green-600'
    ];
    return colors[index] || 'from-slate-500 to-slate-600';
  };

  // Interactive inline SVG line chart (no external deps)
  const LineChart = ({ data = [], height = 160 }) => {
    const [hoverIndex, setHoverIndex] = useState(null);
    const [tooltip, setTooltip] = useState({ visible: false, x: 0, y: 0 });
    const containerRef = useRef(null);

    if (!data || data.length === 0) return <div className="text-sm text-slate-500">No trend data</div>;

    const points = data.map(d => d.amount);
    const max = Math.max(...points);
    const min = Math.min(...points);
    const range = Math.max(1, max - min);

    const padding = 20;
    const w = Math.max(300, data.length * 36);
    const h = height;
    const stepX = (w - padding * 2) / Math.max(1, data.length - 1);

    const xy = data.map((d, i) => {
      const x = padding + i * stepX;
      const y = padding + ((max - d.amount) / range) * (h - padding * 2);
      return { x, y, label: d.date, value: d.amount };
    });

    const pathD = xy.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ');
    const areaD = `${xy.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ')} L ${xy[xy.length - 1].x} ${h - padding} L ${xy[0].x} ${h - padding} Z`;

    const handleMouseMove = (e) => {
      const rect = e.currentTarget.getBoundingClientRect();
      const clientX = e.clientX;
      const x = clientX - rect.left;
      const ratio = (x - (rect.width * (padding / w))) / (rect.width - rect.width * (padding * 2 / w));
      const idx = Math.round(ratio * (data.length - 1));
      const clamped = Math.max(0, Math.min(data.length - 1, idx));
      setHoverIndex(clamped);
      const p = xy[clamped];
      setTooltip({ visible: true, x: p.x, y: p.y });
    };

    const handleMouseLeave = () => {
      setHoverIndex(null);
      setTooltip({ visible: false, x: 0, y: 0 });
    };

    return (
      <div className="w-full overflow-x-auto relative" ref={containerRef}>
        <svg
          viewBox={`0 0 ${w} ${h}`}
          className="w-full"
          preserveAspectRatio="xMinYMin meet"
          onMouseMove={handleMouseMove}
          onMouseLeave={handleMouseLeave}
        >
          <defs>
            <linearGradient id="trendGrad" x1="0" x2="0" y1="0" y2="1">
              <stop offset="0%" stopColor="#60a5fa" stopOpacity="0.9" />
              <stop offset="100%" stopColor="#a78bfa" stopOpacity="0.1" />
            </linearGradient>
          </defs>

          {/* area */}
          <path d={areaD} fill="url(#trendGrad)" stroke="none" />

          {/* line */}
          <path d={pathD} fill="none" stroke="#4f46e5" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />

          {/* vertical hover line + highlight */}
          {hoverIndex !== null && (
            <g>
              <line x1={xy[hoverIndex].x} x2={xy[hoverIndex].x} y1={padding} y2={h - padding} stroke="#a78bfa" strokeWidth={1} strokeDasharray="4 4" />
              <circle cx={xy[hoverIndex].x} cy={xy[hoverIndex].y} r={5} fill="#fff" stroke="#4f46e5" strokeWidth={2} />
            </g>
          )}

          {/* points (reduce DOM by small circles) */}
          {xy.map((p, i) => (
            <circle key={i} cx={p.x} cy={p.y} r={2.5} fill="#4f46e5" />
          ))}
        </svg>

        {/* Tooltip positioned using percentage so it scales with responsive SVG */}
        {tooltip.visible && (
          <div
            className="absolute -translate-x-1/2 bg-white border rounded shadow px-2 py-1 text-xs pointer-events-none"
            style={{ left: `${(tooltip.x / w) * 100}%`, top: `${(tooltip.y / h) * 100}%`, transform: 'translate(-50%, -120%)' }}
          >
            <div className="font-medium text-slate-900">₹{xy[hoverIndex].value.toLocaleString()}</div>
            <div className="text-slate-500">{new Date(xy[hoverIndex].label).toLocaleDateString('en-IN')}</div>
          </div>
        )}

        {/* Date labels aligned under each data point using percentage left */}
        <div className="relative mt-2 h-6">
          {xy.map((p, i) => (
            <div
              key={i}
              className="absolute text-xs text-slate-500"
              style={{ left: `${(p.x / w) * 100}%`, transform: 'translateX(-50%)' }}
              title={new Date(p.label).toLocaleDateString()}
            >
              {new Date(p.label).getDate()}
            </div>
          ))}
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Mobile Header */}
      <div className="lg:hidden bg-white shadow-sm border-b px-4 py-3 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            data-testid="mobile-menu-btn"
          >
            <Menu className="h-5 w-5" />
          </Button>
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-lg flex items-center justify-center">
              <Brain className="h-5 w-5 text-white" />
            </div>
            <span className="font-bold text-lg text-slate-900">SpendSmart AI</span>
          </div>
        </div>
        <Button variant="ghost" size="sm" onClick={onLogout} data-testid="mobile-logout-btn">
          <LogOut className="h-4 w-4" />
        </Button>
      </div>

      <div className="flex">
        {/* Sidebar */}
        <div className={`${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} lg:translate-x-0 fixed lg:static inset-y-0 left-0 z-50 w-64 bg-white shadow-xl transition-transform duration-300 ease-in-out`}>
          <div className="p-6">
            <div className="flex items-center space-x-2 mb-8">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-lg flex items-center justify-center">
                <Brain className="h-6 w-6 text-white" />
              </div>
              <span className="font-bold text-xl text-slate-900">SpendSmart AI</span>
            </div>
            
            <nav className="space-y-2">
              {sidebarItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                    item.active 
                      ? 'bg-gradient-to-r from-blue-600 to-indigo-700 text-white' 
                      : 'text-slate-600 hover:bg-slate-100'
                  }`}
                  data-testid={`sidebar-${item.label.toLowerCase().replace(' ', '-')}`}
                >
                  <item.icon className="h-5 w-5" />
                  <span className="font-medium">{item.label}</span>
                </Link>
              ))}
            </nav>
          </div>
          
          {/* User Profile */}
          <div className="absolute bottom-0 left-0 right-0 p-6 border-t">
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-blue-600 rounded-full flex items-center justify-center">
                <span className="text-white font-semibold">{user.name[0]}</span>
              </div>
              <div>
                <p className="font-medium text-slate-900">{user.name}</p>
                <p className="text-sm text-slate-600">{user.email}</p>
              </div>
            </div>
            <Button 
              onClick={onLogout} 
              variant="outline" 
              className="w-full"
              data-testid="sidebar-logout-btn"
            >
              <LogOut className="h-4 w-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 lg:ml-0">
          <div className="p-6">
            {/* Header */}
            <div className="mb-8">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <h1 className="text-3xl font-bold text-slate-900 mb-2" data-testid="analytics-title">
                    Financial Analytics 📈
                  </h1>
                  <p className="text-slate-600">
                    Detailed insights into your spending patterns and trends
                  </p>
                </div>
                
                <div className="flex items-center space-x-2 mt-4 sm:mt-0">
                  <Filter className="h-4 w-4 text-slate-500" />
                  <select 
                    value={selectedPeriod} 
                    onChange={(e) => setSelectedPeriod(Number(e.target.value))}
                    className="px-3 py-2 border border-slate-300 rounded-lg bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    data-testid="period-selector"
                  >
                    <option value={7}>Last 7 days</option>
                    <option value={30}>Last 30 days</option>
                    <option value={90}>Last 3 months</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Summary Overview */}
            {summary && (
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6 mb-8">
                <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow" data-testid="expenses-overview-card">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-slate-600 flex items-center">
                      <TrendingDown className="h-4 w-4 mr-2 text-red-600" />
                      Total Expenses
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-3xl font-bold text-slate-900 mb-1">
                      ₹{summary.total_expenses.toLocaleString()}
                    </div>
                    <p className="text-sm text-slate-600">
                      {summary.transaction_count} transactions
                    </p>
                  </CardContent>
                </Card>

                <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow" data-testid="income-overview-card">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-slate-600 flex items-center">
                      <TrendingUp className="h-4 w-4 mr-2 text-green-600" />
                      Total Income
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-3xl font-bold text-slate-900 mb-1">
                      ₹{summary.total_income.toLocaleString()}
                    </div>
                    <p className="text-sm text-slate-600">
                      Active income streams
                    </p>
                  </CardContent>
                </Card>

                <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow" data-testid="savings-overview-card">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-slate-600 flex items-center">
                      <PieChart className="h-4 w-4 mr-2 text-blue-600" />
                      Net Savings
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className={`text-3xl font-bold mb-1 ${
                      summary.net_savings >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      ₹{summary.net_savings.toLocaleString()}
                    </div>
                    <p className="text-sm text-slate-600">
                      {((summary.net_savings / summary.total_income) * 100).toFixed(1)}% savings rate
                    </p>
                  </CardContent>
                </Card>

                <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow" data-testid="invested-overview-card">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-slate-600 flex items-center">
                      <ArrowUpRight className="h-4 w-4 mr-2 text-emerald-600" />
                      Invested Amount
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-3xl font-bold text-slate-900 mb-1">
                      ₹{(summary.invested_amount ?? 0).toLocaleString()}
                    </div>
                    <p className="text-sm text-slate-600">
                      {summary.investment_transaction_count ? `${summary.investment_transaction_count} transactions` : 'Build your investment trail'}
                    </p>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Spending Trends Chart */}
            {trends && (
              <div className="mb-8">
                <Card className="border-0 shadow-lg" data-testid="spending-trends-card">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <BarChart3 className="h-5 w-5 text-blue-600" />
                      <span>Daily Spending Trends</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div>
                      <LineChart data={trends.trends.slice(-14)} height={200} />
                    </div>
                    <div className="mt-4 p-4 bg-slate-50 rounded-lg">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-slate-600">Average Daily Spending:</span>
                        <span className="font-semibold text-slate-900">₹{trends.average_daily_spending.toLocaleString()}</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Category Breakdown */}
            {summary && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Category List */}
                <Card className="border-0 shadow-lg" data-testid="category-breakdown-card">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <PieChart className="h-5 w-5 text-indigo-600" />
                      <span>Spending by Category</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {summary.top_categories.map((category, index) => (
                      <div key={index} className="relative" data-testid={`category-item-${index}`}>
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center space-x-3">
                            <div className="text-2xl">{getCategoryIcon(category.category)}</div>
                            <div>
                              <div className="font-medium text-slate-900">{category.category}</div>
                              <div className="text-sm text-slate-600">{category.percentage}% of total</div>
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="font-bold text-slate-900">₹{category.amount.toLocaleString()}</div>
                          </div>
                        </div>
                        
                        {/* Progress Bar */}
                        <div className="w-full bg-slate-200 rounded-full h-2">
                          <div 
                            className={`bg-gradient-to-r ${getCategoryColor(index)} h-2 rounded-full transition-all duration-700 ease-out`}
                            style={{ width: `${category.percentage}%` }}
                          ></div>
                        </div>
                      </div>
                    ))}
                    {summary.investment_category && !summary.top_categories.some((cat) => cat.category === 'Investments') && (
                      <div className="relative border-t pt-4" data-testid="category-item-investments">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center space-x-3">
                            <div className="text-2xl">{getCategoryIcon('Investments')}</div>
                            <div>
                              <div className="font-medium text-slate-900">{summary.investment_category.category}</div>
                              <div className="text-sm text-slate-600">{summary.investment_category.percentage}% of total</div>
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="font-bold text-slate-900">₹{summary.investment_category.amount.toLocaleString()}</div>
                          </div>
                        </div>

                        <div className="w-full bg-slate-200 rounded-full h-2">
                          <div 
                            className="bg-gradient-to-r from-emerald-500 to-emerald-600 h-2 rounded-full transition-all duration-700 ease-out"
                            style={{ width: `${summary.investment_category.percentage}%` }}
                          ></div>
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Category Insights */}
                <Card className="border-0 shadow-lg" data-testid="category-insights-card">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <Brain className="h-5 w-5 text-purple-600" />
                      <span>Smart Insights</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {summary.investment_category && (
                      <div className="p-4 bg-gradient-to-r from-emerald-50 to-green-50 rounded-lg">
                        <div className="flex items-start space-x-3">
                          <div className="text-2xl">{getCategoryIcon('Investments')}</div>
                          <div>
                            <div className="font-semibold text-slate-900 mb-1">
                              Investment Spotlight
                            </div>
                            <div className="text-sm text-slate-600">
                              You allocated <span className="font-medium text-emerald-700">₹{summary.investment_category.amount.toLocaleString()}</span> towards investments, representing {summary.investment_category.percentage}% of your outflow this period.
                            </div>
                          </div>
                        </div>
                      </div>
                    )}

                    {summary.top_categories.length > 0 && (
                      <>
                        <div className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg">
                          <div className="flex items-start space-x-3">
                            <div className="text-2xl">{getCategoryIcon(summary.top_categories[0].category)}</div>
                            <div>
                              <div className="font-semibold text-slate-900 mb-1">
                                Top Spending Category
                              </div>
                              <div className="text-sm text-slate-600">
                                You spent <span className="font-medium text-blue-700">₹{summary.top_categories[0].amount.toLocaleString()}</span> on {summary.top_categories[0].category}, which is {summary.top_categories[0].percentage}% of your total expenses.
                              </div>
                            </div>
                          </div>
                        </div>

                        <div className="p-4 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg">
                          <div className="flex items-start space-x-3">
                            <div className="text-2xl">💰</div>
                            <div>
                              <div className="font-semibold text-slate-900 mb-1">
                                Savings Opportunity
                              </div>
                              <div className="text-sm text-slate-600">
                                {summary.net_savings >= 0 
                                  ? `Great job! You saved ₹${summary.net_savings.toLocaleString()} this month.`
                                  : `Consider reducing ${summary.top_categories[0].category} expenses by 10% to improve your savings.`
                                }
                              </div>
                            </div>
                          </div>
                        </div>

                        <div className="p-4 bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg">
                          <div className="flex items-start space-x-3">
                            <div className="text-2xl">📈</div>
                            <div>
                              <div className="font-semibold text-slate-900 mb-1">
                                Spending Pattern
                              </div>
                              <div className="text-sm text-slate-600">
                                You made {summary.transaction_count} transactions with an average of ₹{Math.round(summary.total_expenses / summary.transaction_count).toLocaleString()} per transaction.
                              </div>
                            </div>
                          </div>
                        </div>
                      </>
                    )}
                    
                    <div className="pt-4 border-t">
                      <Link to="/insights">
                        <Button variant="outline" className="w-full" data-testid="get-ai-insights-btn">
                          Get Detailed AI Analysis
                          <ArrowUpRight className="h-4 w-4 ml-2" />
                        </Button>
                      </Link>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden" 
          onClick={() => setSidebarOpen(false)}
          data-testid="sidebar-overlay"
        ></div>
      )}
    </div>
  );
};

export default Analytics;