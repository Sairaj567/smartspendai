import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Upload, 
  FileText, 
  CheckCircle, 
  AlertCircle, 
  Download,
  Info,
  X,
  Menu,
  LogOut,
  Home,
  BarChart3,
  Receipt,
  Brain,
  CreditCard
} from 'lucide-react';
import { Link } from 'react-router-dom';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ImportTransactions = ({ user, onLogout, onImportComplete }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [importing, setImporting] = useState(false);
  const [importResult, setImportResult] = useState(null);
  const [skipDuplicates, setSkipDuplicates] = useState(true);
  const [showPreview, setShowPreview] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const sidebarItems = [
    { icon: Home, label: 'Dashboard', path: '/dashboard' },
    { icon: BarChart3, label: 'Analytics', path: '/analytics' },
    { icon: Receipt, label: 'Transactions', path: '/transactions' },
    { icon: Upload, label: 'Import', path: '/import', active: true },
    { icon: Brain, label: 'AI Insights', path: '/insights' },
    { icon: CreditCard, label: 'Pay', path: '/pay' }
  ];

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      // Validate file type
      const validTypes = ['.csv', '.xlsx', '.xls'];
      const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
      
      if (!validTypes.includes(fileExtension)) {
        alert('Please select a CSV or Excel file (.csv, .xlsx, .xls)');
        return;
      }
      
      setSelectedFile(file);
      setImportResult(null);
    }
  };

  const handleImport = async () => {
    if (!selectedFile) return;

    setImporting(true);
    
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('skip_duplicates', skipDuplicates);

      const response = await axios.post(
        `${API}/transactions/import/${user.id}?skip_duplicates=${skipDuplicates}`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      setImportResult(response.data);
      
      // Notify parent component of successful import
      if (onImportComplete && response.data.successful_imports > 0) {
        onImportComplete(response.data);
      }

    } catch (error) {
      console.error('Import failed:', error);
      setImportResult({
        total_rows: 0,
        successful_imports: 0,
        failed_imports: 1,
        errors: [error.response?.data?.detail || 'Import failed. Please try again.'],
        duplicate_count: 0,
        imported_transactions: []
      });
    } finally {
      setImporting(false);
    }
  };

  const resetImport = () => {
    setSelectedFile(null);
    setImportResult(null);
    setShowPreview(false);
    // Reset file input
    const fileInput = document.getElementById('file-input');
    if (fileInput) fileInput.value = '';
  };

  const downloadSampleCSV = () => {
    const sampleData = `Date,Amount,Description,Merchant,Payment Method,Category
2024-01-15,250.00,Lunch at restaurant,Pizza Hut,UPI,Food & Dining
2024-01-16,50.00,Metro travel,Delhi Metro,Card,Transportation
2024-01-17,1200.00,Grocery shopping,BigBazaar,UPI,Shopping
2024-01-18,150.00,Mobile recharge,Airtel,UPI,Bills & Utilities
2024-01-19,45000.00,Monthly salary,Company ABC,Bank Transfer,Income`;

    const blob = new Blob([sampleData], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'sample_transactions.csv';
    a.click();
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0`}>
        <div className="flex items-center justify-between h-16 px-6 border-b">
          <span className="text-xl font-bold text-gray-800">SmartSpendAI</span>
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden"
          >
            <X className="h-6 w-6" />
          </button>
        </div>
        
        <nav className="mt-6">
          {sidebarItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center px-6 py-3 text-gray-700 hover:bg-gray-100 ${
                item.active ? 'bg-blue-50 text-blue-600 border-r-2 border-blue-600' : ''
              }`}
            >
              <item.icon className="h-5 w-5 mr-3" />
              {item.label}
            </Link>
          ))}
        </nav>
        
        <div className="absolute bottom-0 w-full p-6 border-t">
          <div className="flex items-center mb-4">
            <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white text-sm font-medium">
              {user?.name?.charAt(0) || 'U'}
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-700">{user?.name || 'User'}</p>
              <p className="text-xs text-gray-500">{user?.email || 'user@example.com'}</p>
            </div>
          </div>
          <button
            onClick={onLogout}
            className="flex items-center w-full px-3 py-2 text-gray-700 hover:bg-gray-100 rounded-md"
          >
            <LogOut className="h-4 w-4 mr-2" />
            Logout
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="bg-white shadow-sm border-b px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <button
                onClick={() => setSidebarOpen(true)}
                className="lg:hidden mr-3"
              >
                <Menu className="h-6 w-6" />
              </button>
              <div>
                <h2 className="text-2xl font-bold text-gray-900">Import Transactions</h2>
                <p className="text-gray-600">Upload your transaction history from CSV or Excel files</p>
              </div>
            </div>
          </div>
        </header>

        {/* Content */}
        <main className="flex-1 overflow-y-auto p-6">
          <div className="max-w-4xl mx-auto space-y-6">

      {/* Instructions Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Info className="h-5 w-5 text-blue-600" />
            File Format Guidelines
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <h4 className="font-semibold mb-2">Supported Columns:</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• <strong>Date</strong> (required): Transaction date</li>
                <li>• <strong>Amount</strong> (required): Transaction amount</li>
                <li>• <strong>Description</strong>: Transaction details</li>
                <li>• <strong>Merchant</strong>: Payee/Store name</li>
                <li>• <strong>Category</strong>: Expense category (auto-detected if missing)</li>
                <li>• <strong>Payment Method</strong>: UPI, Card, Cash, etc.</li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-2">Supported Formats:</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• CSV files (.csv)</li>
                <li>• Excel files (.xlsx, .xls)</li>
                <li>• Date formats: DD/MM/YYYY, MM/DD/YYYY, YYYY-MM-DD</li>
                <li>• Amount: Numbers with or without ₹ symbol</li>
              </ul>
            </div>
          </div>
          
          <div className="flex gap-2 pt-4 border-t">
            <Button 
              variant="outline" 
              size="sm" 
              onClick={downloadSampleCSV}
              className="flex items-center gap-2"
            >
              <Download className="h-4 w-4" />
              Download Sample CSV
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Upload Card */}
      <Card>
        <CardHeader>
          <CardTitle>Upload File</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {!selectedFile ? (
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
              <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <div className="space-y-2">
                <p className="text-lg font-medium">Choose a file to upload</p>
                <p className="text-gray-500">CSV or Excel files up to 10MB</p>
              </div>
              <input
                id="file-input"
                type="file"
                accept=".csv,.xlsx,.xls"
                onChange={handleFileSelect}
                className="hidden"
              />
              <Button 
                onClick={() => document.getElementById('file-input').click()}
                className="mt-4"
              >
                Select File
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 border rounded-lg bg-gray-50">
                <div className="flex items-center gap-3">
                  <FileText className="h-8 w-8 text-blue-600" />
                  <div>
                    <p className="font-medium">{selectedFile.name}</p>
                    <p className="text-sm text-gray-500">
                      {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={resetImport}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>

              {/* Options */}
              <div className="space-y-3">
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="skip-duplicates"
                    checked={skipDuplicates}
                    onChange={(e) => setSkipDuplicates(e.target.checked)}
                    className="rounded"
                  />
                  <label htmlFor="skip-duplicates" className="text-sm">
                    Skip duplicate transactions (recommended)
                  </label>
                </div>
              </div>

              {/* Import Button */}
              <Button
                onClick={handleImport}
                disabled={importing}
                className="w-full"
              >
                {importing ? 'Importing...' : 'Import Transactions'}
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Results Card */}
      {importResult && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {importResult.successful_imports > 0 ? (
                <CheckCircle className="h-5 w-5 text-green-600" />
              ) : (
                <AlertCircle className="h-5 w-5 text-red-600" />
              )}
              Import Results
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Summary */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-3 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">
                  {importResult.total_rows}
                </div>
                <div className="text-sm text-gray-600">Total Rows</div>
              </div>
              
              <div className="text-center p-3 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">
                  {importResult.successful_imports}
                </div>
                <div className="text-sm text-gray-600">Imported</div>
              </div>
              
              <div className="text-center p-3 bg-yellow-50 rounded-lg">
                <div className="text-2xl font-bold text-yellow-600">
                  {importResult.duplicate_count}
                </div>
                <div className="text-sm text-gray-600">Duplicates</div>
              </div>
              
              <div className="text-center p-3 bg-red-50 rounded-lg">
                <div className="text-2xl font-bold text-red-600">
                  {importResult.failed_imports + importResult.errors.length}
                </div>
                <div className="text-sm text-gray-600">Errors</div>
              </div>
            </div>

            {/* Errors */}
            {importResult.errors.length > 0 && (
              <Alert>
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>
                  <div className="space-y-1">
                    <p className="font-medium">Import Errors:</p>
                    <ul className="text-sm space-y-1">
                      {importResult.errors.slice(0, 5).map((error, index) => (
                        <li key={index}>• {error}</li>
                      ))}
                      {importResult.errors.length > 5 && (
                        <li>... and {importResult.errors.length - 5} more errors</li>
                      )}
                    </ul>
                  </div>
                </AlertDescription>
              </Alert>
            )}

            {/* Success Message */}
            {importResult.successful_imports > 0 && (
              <Alert>
                <CheckCircle className="h-4 w-4" />
                <AlertDescription>
                  Successfully imported {importResult.successful_imports} transactions!
                  {importResult.duplicate_count > 0 && (
                    ` ${importResult.duplicate_count} duplicates were skipped.`
                  )}
                </AlertDescription>
              </Alert>
            )}

            {/* Preview */}
            {importResult.imported_transactions.length > 0 && (
              <div className="space-y-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowPreview(!showPreview)}
                >
                  {showPreview ? 'Hide' : 'Show'} Preview
                </Button>
                
                {showPreview && (
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b">
                          <th className="text-left p-2">Date</th>
                          <th className="text-left p-2">Amount</th>
                          <th className="text-left p-2">Description</th>
                          <th className="text-left p-2">Category</th>
                        </tr>
                      </thead>
                      <tbody>
                        {importResult.imported_transactions.slice(0, 5).map((tx, index) => (
                          <tr key={index} className="border-b">
                            <td className="p-2">{new Date(tx.date).toLocaleDateString()}</td>
                            <td className="p-2">₹{tx.amount}</td>
                            <td className="p-2 truncate max-w-xs">{tx.description}</td>
                            <td className="p-2">
                              <Badge variant="outline" className="text-xs">
                                {tx.category}
                              </Badge>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )}

            {/* Actions */}
            <div className="flex gap-2 pt-4 border-t">
              <Button onClick={resetImport} variant="outline">
                Import Another File
              </Button>
              {importResult.successful_imports > 0 && onImportComplete && (
                <Button onClick={() => onImportComplete(importResult)}>
                  View Transactions
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      )}
          </div>
        </main>
      </div>
    </div>
  );
};

export default ImportTransactions;