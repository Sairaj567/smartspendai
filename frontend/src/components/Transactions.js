import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { 
  Receipt, 
  Search, 
  Filter, 
  Download,
  Brain,
  Menu,
  LogOut,
  Home,
  BarChart3,
  CreditCard,
  Calendar,
  TrendingUp,
  TrendingDown,
  ArrowUpRight,
  ArrowDownRight
} from 'lucide-react';
import { Link } from 'react-router-dom';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Transactions = ({ user, onLogout }) => {
  const [transactions, setTransactions] = useState([]);
  const [filteredTransactions, setFilteredTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedType, setSelectedType] = useState('all');

  useEffect(() => {
    loadTransactions();
  }, [user]);

  useEffect(() => {
    filterTransactions();
  }, [transactions, searchQuery, selectedCategory, selectedType]);

  const loadTransactions = async () => {
    try {
      const response = await axios.get(`${API}/transactions/${user.id}?limit=100`);
      setTransactions(response.data);
    } catch (error) {
      console.error('Error loading transactions:', error);
    } finally {
      setLoading(false);
    }
  };

  const filterTransactions = () => {
    let filtered = transactions;
    
    // Search filter
    if (searchQuery) {
      filtered = filtered.filter(tx => 
        tx.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        tx.merchant.toLowerCase().includes(searchQuery.toLowerCase()) ||
        tx.category.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }
    
    // Category filter
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(tx => tx.category === selectedCategory);
    }
    
    // Type filter
    if (selectedType !== 'all') {
      filtered = filtered.filter(tx => tx.type === selectedType);
    }
    
    setFilteredTransactions(filtered);
  };

  const sidebarItems = [
    { icon: Home, label: 'Dashboard', path: '/dashboard' },
    { icon: BarChart3, label: 'Analytics', path: '/analytics' },
    { icon: Receipt, label: 'Transactions', path: '/transactions', active: true },
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
      'Transfer': '🔄'
    };
    return icons[category] || '💳';
  };

  const getCategoryColor = (category) => {
    const colors = {
      'Food & Dining': 'bg-orange-100 text-orange-800',
      'Transportation': 'bg-blue-100 text-blue-800',
      'Shopping': 'bg-purple-100 text-purple-800',
      'Entertainment': 'bg-pink-100 text-pink-800',
      'Bills & Utilities': 'bg-yellow-100 text-yellow-800',
      'Healthcare': 'bg-green-100 text-green-800',
      'Education': 'bg-indigo-100 text-indigo-800',
      'Income': 'bg-emerald-100 text-emerald-800',
      'Transfer': 'bg-slate-100 text-slate-800'
    };
    return colors[category] || 'bg-gray-100 text-gray-800';
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = (now - date) / (1000 * 60 * 60);
    
    if (diffInHours < 24) {
      return `${Math.floor(diffInHours)}h ago`;
    } else if (diffInHours < 48) {
      return 'Yesterday';
    } else {
      return date.toLocaleDateString('en-IN', { 
        day: 'numeric', 
        month: 'short' 
      });
    }
  };

  const formatTime = (dateString) => {
    return new Date(dateString).toLocaleTimeString('en-IN', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getUniqueCategories = () => {
    const categories = [...new Set(transactions.map(tx => tx.category))];
    return categories.sort();
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
              <h1 className="text-3xl font-bold text-slate-900 mb-2" data-testid="transactions-title">
                Transaction History 📋
              </h1>
              <p className="text-slate-600">
                Track and analyze all your financial transactions
              </p>
            </div>

            {/* Filters */}
            <Card className="border-0 shadow-lg mb-8" data-testid="filters-card">
              <CardContent className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  {/* Search */}
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
                    <Input
                      placeholder="Search transactions..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-10"
                      data-testid="search-input"
                    />
                  </div>
                  
                  {/* Category Filter */}
                  <select 
                    value={selectedCategory} 
                    onChange={(e) => setSelectedCategory(e.target.value)}
                    className="px-3 py-2 border border-slate-300 rounded-lg bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    data-testid="category-filter"
                  >
                    <option value="all">All Categories</option>
                    {getUniqueCategories().map(category => (
                      <option key={category} value={category}>{category}</option>
                    ))}
                  </select>
                  
                  {/* Type Filter */}
                  <select 
                    value={selectedType} 
                    onChange={(e) => setSelectedType(e.target.value)}
                    className="px-3 py-2 border border-slate-300 rounded-lg bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    data-testid="type-filter"
                  >
                    <option value="all">All Types</option>
                    <option value="expense">Expenses</option>
                    <option value="income">Income</option>
                  </select>
                  
                  {/* Export */}
                  <Button variant="outline" className="flex items-center space-x-2" data-testid="export-btn">
                    <Download className="h-4 w-4" />
                    <span>Export</span>
                  </Button>
                </div>
                
                {/* Filter Summary */}
                <div className="mt-4 flex items-center space-x-4 text-sm text-slate-600">
                  <span>Showing {filteredTransactions.length} of {transactions.length} transactions</span>
                  {(searchQuery || selectedCategory !== 'all' || selectedType !== 'all') && (
                    <Button 
                      variant="ghost" 
                      size="sm"
                      onClick={() => {
                        setSearchQuery('');
                        setSelectedCategory('all');
                        setSelectedType('all');
                      }}
                      data-testid="clear-filters-btn"
                    >
                      Clear Filters
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Transaction List */}
            <Card className="border-0 shadow-lg" data-testid="transactions-list-card">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Receipt className="h-5 w-5 text-blue-600" />
                  <span>Recent Transactions</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                {filteredTransactions.length === 0 ? (
                  <div className="text-center py-12" data-testid="no-transactions">
                    <Receipt className="h-12 w-12 text-slate-400 mx-auto mb-4" />
                    <p className="text-slate-600 mb-2">No transactions found</p>
                    <p className="text-sm text-slate-500">Try adjusting your filters or search terms</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {filteredTransactions.map((transaction, index) => (
                      <div 
                        key={transaction.id} 
                        className="flex items-center justify-between p-4 bg-white border border-slate-200 rounded-lg hover:shadow-md transition-shadow cursor-pointer"
                        data-testid={`transaction-${index}`}
                      >
                        <div className="flex items-center space-x-4">
                          {/* Category Icon */}
                          <div className="w-12 h-12 bg-gradient-to-br from-slate-100 to-slate-200 rounded-full flex items-center justify-center text-xl">
                            {getCategoryIcon(transaction.category)}
                          </div>
                          
                          {/* Transaction Details */}
                          <div>
                            <div className="flex items-center space-x-2 mb-1">
                              <h3 className="font-semibold text-slate-900">{transaction.merchant}</h3>
                              <Badge className={getCategoryColor(transaction.category)} variant="secondary">
                                {transaction.category}
                              </Badge>
                            </div>
                            <p className="text-sm text-slate-600">{transaction.description}</p>
                            <div className="flex items-center space-x-4 mt-1 text-xs text-slate-500">
                              <span className="flex items-center space-x-1">
                                <Calendar className="h-3 w-3" />
                                <span>{formatDate(transaction.date)}</span>
                              </span>
                              <span>{formatTime(transaction.date)}</span>
                              <span>{transaction.payment_method}</span>
                              {transaction.location && <span>{transaction.location}</span>}
                            </div>
                          </div>
                        </div>
                        
                        {/* Amount */}
                        <div className="text-right">
                          <div className={`text-lg font-bold flex items-center ${
                            transaction.type === 'income' ? 'text-green-600' : 'text-slate-900'
                          }`}>
                            {transaction.type === 'income' ? (
                              <ArrowDownRight className="h-4 w-4 mr-1 text-green-600" />
                            ) : (
                              <ArrowUpRight className="h-4 w-4 mr-1 text-red-600" />
                            )}
                            ₹{transaction.amount.toLocaleString()}
                          </div>
                          <div className="text-xs text-slate-500 mt-1">
                            {transaction.type === 'income' ? 'Credit' : 'Debit'}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
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

export default Transactions;