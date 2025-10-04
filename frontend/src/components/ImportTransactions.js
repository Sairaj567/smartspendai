import React, { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  CardDescription,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Upload,
  BarChart3,
  Brain,
  CreditCard,
  Home,
  LogOut,
  Menu,
  Receipt,
  Info,
  CheckCircle,
  AlertCircle,
  FileText,
  Download,
} from 'lucide-react';

const resolveApiBase = () => {
  const envBase = process.env.REACT_APP_BACKEND_URL;
  if (envBase) {
    return `${envBase.replace(/\/$/, '')}/api`;
  }

  if (typeof window !== 'undefined') {
    const { protocol } = window.location;
    return `${protocol}//localhost:8000/api`;
  }

  return 'http://localhost:8000/api';
};

const API_BASE = resolveApiBase();
const allowedExtensions = ['.csv', '.xlsx', '.xls'];

const navItems = [
  { icon: Home, label: 'Dashboard', path: '/dashboard' },
  { icon: BarChart3, label: 'Analytics', path: '/analytics' },
  { icon: Receipt, label: 'Transactions', path: '/transactions' },
  { icon: Upload, label: 'Import', path: '/import', active: true },
  { icon: Brain, label: 'AI Insights', path: '/insights' },
  { icon: CreditCard, label: 'Pay', path: '/pay' },
];

const sampleCsv = `Tran Date,Chq No,Particulars,Debit,Credit,Balance,Init. Br\n2024-04-01,123456,Rent Payment,25000.00,,150000.00,175000.00\n2024-04-02,,Salary Credit,,75000.00,225000.00,\n2024-04-03,,Grocery Store,3200.50,,221799.50,\n2024-04-04,555555,Utility Bill,2450.00,,219349.50,\n2024-04-05,,Movie Night,1200.00,,218149.50,\n2024-04-06,,Stock Dividend,,5000.00,223149.50,\n2024-04-07,987654,Travel Booking,8500.00,,214649.50,\n2024-04-08,,Freelance Payment,,15000.00,229649.50,`;

const formatBytes = (bytes) => {
  if (!Number.isFinite(bytes) || bytes <= 0) return '0 B';
  const units = ['B', 'KB', 'MB', 'GB'];
  const index = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
  return `${(bytes / 1024 ** index).toFixed(1)} ${units[index]}`;
};

const describeAxiosError = (error) => {
  if (error?.response) {
    const { status, statusText, data } = error.response;
    const statusLine = `${status}${statusText ? ` ${statusText}` : ''}`;
    const detail = data?.detail || data?.message;
    return detail
      ? `Import failed (${statusLine}). ${detail}`
      : `Import failed (${statusLine}). Check the backend logs for more details.`;
  }

  if (error?.request) {
    return `Import failed: no response received from ${API_BASE}. Verify the backend is reachable.`;
  }

  if (error?.message) {
    return `Import failed: ${error.message}`;
  }

  return 'Import failed due to an unknown error. Please try again.';
};

function ImportTransactions({ user, onLogout, onImportComplete }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [skipDuplicates, setSkipDuplicates] = useState(true);
  const [isImporting, setIsImporting] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const fileMetadata = useMemo(() => {
    if (!selectedFile) return null;
    return {
      name: selectedFile.name,
      size: formatBytes(selectedFile.size),
      type: selectedFile.type || 'Unknown',
      lastModified: new Date(selectedFile.lastModified).toLocaleString(),
    };
  }, [selectedFile]);

  const handleFileChange = (event) => {
    const file = event.target.files?.[0];
    setResult(null);
    setError(null);

    if (!file) {
      setSelectedFile(null);
      return;
    }

    const extension = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
    if (!allowedExtensions.includes(extension)) {
      setError(`Unsupported file type. Allowed: ${allowedExtensions.join(', ')}`);
      setSelectedFile(null);
      return;
    }

    setSelectedFile(file);
  };

  const handleDownloadSample = () => {
    const blob = new Blob([sampleCsv], { type: 'text/csv;charset=utf-8;' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'sample_transactions.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  };

  const handleImport = async () => {
    if (!selectedFile) {
      setError('Please choose a CSV or Excel file first.');
      return;
    }

    if (!user?.id) {
      setError('User information is missing. Please sign in again.');
      return;
    }

    setIsImporting(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('skip_duplicates', skipDuplicates);

      const response = await axios.post(
        `${API_BASE}/transactions/import/${user.id}?skip_duplicates=${skipDuplicates}`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      setResult(response.data);
      if (typeof onImportComplete === 'function') {
        onImportComplete(response.data);
      }
    } catch (err) {
      console.error('Import failed:', err);
      setError(describeAxiosError(err));
    } finally {
      setIsImporting(false);
    }
  };

  return (
    <div className="flex h-screen bg-slate-50">
      <aside
        className={`${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        } fixed inset-y-0 left-0 z-40 w-64 bg-white shadow-lg transition-transform duration-300 ease-in-out lg:static lg:translate-x-0`}
      >
        <div className="flex items-center justify-between h-16 px-6 border-b">
          <span className="text-xl font-semibold text-slate-900">SmartSpendAI</span>
          <button className="lg:hidden" onClick={() => setSidebarOpen(false)}>
            <Menu className="h-5 w-5" />
          </button>
        </div>
        <nav className="p-4 space-y-1">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors ${
                item.active
                  ? 'bg-blue-50 text-blue-600 border-r-2 border-blue-600'
                  : 'text-slate-600 hover:bg-slate-100'
              }`}
            >
              <item.icon className="h-4 w-4" />
              {item.label}
            </Link>
          ))}
        </nav>
        <div className="absolute bottom-0 w-full border-t px-4 py-5 space-y-3">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-blue-600 text-sm font-semibold text-white">
              {user?.name?.[0]?.toUpperCase() || 'U'}
            </div>
            <div>
              <p className="text-sm font-semibold text-slate-900">{user?.name || 'User'}</p>
              <p className="text-xs text-slate-500">{user?.email || 'user@example.com'}</p>
            </div>
          </div>
          <Button variant="outline" className="w-full" onClick={onLogout}>
            <LogOut className="mr-2 h-4 w-4" />
            Logout
          </Button>
        </div>
      </aside>

      <main className="flex-1 overflow-y-auto">
        <header className="sticky top-0 z-10 bg-white/80 backdrop-blur border-b">
          <div className="flex items-center justify-between px-6 py-4">
            <div className="flex items-center gap-3">
              <button className="lg:hidden" onClick={() => setSidebarOpen(true)}>
                <Menu className="h-5 w-5" />
              </button>
              <div>
                <h1 className="text-2xl font-bold text-slate-900">Import Transactions</h1>
                <p className="text-sm text-slate-500">
                  Upload your bank statement (.csv / .xlsx) and let SmartSpendAI do the rest
                </p>
              </div>
            </div>
          </div>
        </header>

        <div className="mx-auto max-w-5xl space-y-6 px-6 py-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <Info className="h-4 w-4 text-blue-600" />
                Supported Formats
              </CardTitle>
              <CardDescription>
                We automatically recognise bank exports with headers such as
                <Badge variant="secondary" className="ml-2">
                  Tran Date / Chq No / Particulars / Debit / Credit / Balance / Init. Br
                </Badge>
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4 text-sm text-slate-600">
              <ul className="list-disc space-y-2 pl-4">
                <li>Dates like <strong>05-09-2025</strong> or <strong>2025/09/05</strong> are parsed automatically.</li>
                <li>Multi-line descriptions and cheque numbers are preserved for richer context.</li>
                <li>Debits are treated as expenses, credits as income. Duplicate detection is optional.</li>
              </ul>
              <Button variant="outline" size="sm" onClick={handleDownloadSample}>
                <Download className="mr-2 h-4 w-4" />
                Download sample CSV
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <FileText className="h-4 w-4 text-blue-600" />
                Upload file
              </CardTitle>
              <CardDescription>Choose a CSV or Excel file exported from your bank.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex flex-col items-center justify-center rounded-lg border-2 border-dashed border-slate-300 bg-slate-50 p-8 text-center">
                <Upload className="mb-4 h-10 w-10 text-blue-500" />
                <p className="text-sm text-slate-600">
                  Drag and drop your file here, or click to browse.
                </p>
                <input
                  id="transaction-file"
                  type="file"
                  accept={allowedExtensions.join(',')}
                  className="mt-4"
                  onChange={handleFileChange}
                />
              </div>

              {fileMetadata && (
                <div className="rounded-lg border bg-white p-4 text-sm text-slate-600">
                  <p className="font-medium text-slate-900">Selected file</p>
                  <div className="mt-2 grid gap-1">
                    <span>Name: {fileMetadata.name}</span>
                    <span>Size: {fileMetadata.size}</span>
                    <span>Type: {fileMetadata.type}</span>
                    <span>Last modified: {fileMetadata.lastModified}</span>
                  </div>
                </div>
              )}

              <div className="flex items-center justify-between">
                <label className="flex items-center gap-2 text-sm text-slate-600">
                  <input
                    type="checkbox"
                    checked={skipDuplicates}
                    onChange={(event) => setSkipDuplicates(event.target.checked)}
                  />
                  Skip duplicates (recommended)
                </label>
                <Button onClick={handleImport} disabled={isImporting}>
                  {isImporting ? 'Importing…' : 'Start import'}
                </Button>
              </div>
            </CardContent>
          </Card>

          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {result && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg">
                  <CheckCircle className="h-4 w-4 text-emerald-500" />
                  Import summary
                </CardTitle>
                <CardDescription>
                  {result.successful_imports} transactions saved. {result.duplicate_count} duplicates were skipped.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4 text-sm text-slate-600">
                <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                  <div className="rounded-lg border bg-slate-50 p-4">
                    <p className="text-xs uppercase text-slate-500">Rows processed</p>
                    <p className="text-2xl font-semibold text-slate-900">{result.total_rows}</p>
                  </div>
                  <div className="rounded-lg border bg-slate-50 p-4">
                    <p className="text-xs uppercase text-slate-500">Successful imports</p>
                    <p className="text-2xl font-semibold text-emerald-600">{result.successful_imports}</p>
                  </div>
                </div>
                {Array.isArray(result.errors) && result.errors.length > 0 && (
                  <div>
                    <p className="font-medium text-slate-900">Errors</p>
                    <ul className="mt-2 list-disc space-y-1 pl-5">
                      {result.errors.map((message, index) => (
                        <li key={index}>{message}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </div>
      </main>
    </div>
  );
}

export default ImportTransactions;