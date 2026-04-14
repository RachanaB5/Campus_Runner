/**
 * Report/Statement PDF Template
 * Usage: Order summaries, account statements, sales reports, analytics reports
 * 
 * Dependencies: @react-pdf/renderer
 * 
 * Props:
 * - reportType: 'order-summary' | 'account-statement' | 'sales-report' - Report type
 * - reportTitle: string - Report title
 * - reportPeriod: object - Date range for the report
 * - company: object - Company details
 * - customer: object - Customer details (optional)
 * - summary: object - Key metrics/summary data
 * - transactions: Array - List of transactions/line items
 * - charts: object - Chart data (optional, rendered as tables)
 */

import {
  Document,
  Page,
  Text,
  View,
  StyleSheet,
  Font,
} from '@react-pdf/renderer'

// Register fonts
Font.register({
  family: 'Inter',
  fonts: [
    { src: 'https://fonts.gstatic.com/s/inter/v12/UcCO3FwrK3iLTeHuS_fvQtMwCp50KnMw2boKoduKmMEVuLyfAZ9hjp-Ek-_EeA.woff', fontWeight: 400 },
    { src: 'https://fonts.gstatic.com/s/inter/v12/UcCO3FwrK3iLTeHuS_fvQtMwCp50KnMw2boKoduKmMEVuI6fAZ9hjp-Ek-_EeA.woff', fontWeight: 600 },
    { src: 'https://fonts.gstatic.com/s/inter/v12/UcCO3FwrK3iLTeHuS_fvQtMwCp50KnMw2boKoduKmMEVuFuYAZ9hjp-Ek-_EeA.woff', fontWeight: 700 },
  ],
})

interface Company {
  name: string
  logo?: string
  address?: string
  email?: string
  phone?: string
}

interface Customer {
  name: string
  email: string
  accountId?: string
  memberSince?: string
}

interface ReportPeriod {
  startDate: string
  endDate: string
  label?: string
}

interface SummaryMetric {
  label: string
  value: string | number
  change?: number
  changeLabel?: string
}

interface Transaction {
  date: string
  description: string
  reference?: string
  type: 'credit' | 'debit' | 'order' | 'refund' | 'payment'
  amount: number
  balance?: number
  status?: 'completed' | 'pending' | 'failed'
}

interface CategoryBreakdown {
  category: string
  amount: number
  percentage: number
  count?: number
}

interface ReportStatementPDFProps {
  reportType: 'order-summary' | 'account-statement' | 'sales-report'
  reportTitle: string
  reportId?: string
  generatedDate: string
  reportPeriod: ReportPeriod
  company: Company
  customer?: Customer
  summary: SummaryMetric[]
  transactions: Transaction[]
  categoryBreakdown?: CategoryBreakdown[]
  openingBalance?: number
  closingBalance?: number
  notes?: string
  currency?: string
}

const styles = StyleSheet.create({
  page: {
    fontFamily: 'Inter',
    fontSize: 9,
    padding: 40,
    backgroundColor: '#ffffff',
  },
  // Header
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 30,
    paddingBottom: 20,
    borderBottomWidth: 2,
    borderBottomColor: '#1a1a1a',
  },
  companyInfo: {
    maxWidth: '50%',
  },
  companyName: {
    fontSize: 18,
    fontWeight: 700,
    color: '#1a1a1a',
    marginBottom: 4,
  },
  companyDetails: {
    fontSize: 8,
    color: '#6b7280',
    lineHeight: 1.4,
  },
  reportInfo: {
    textAlign: 'right',
  },
  reportTitle: {
    fontSize: 14,
    fontWeight: 700,
    color: '#1a1a1a',
    marginBottom: 4,
  },
  reportMeta: {
    fontSize: 8,
    color: '#6b7280',
    marginBottom: 2,
  },
  periodBadge: {
    backgroundColor: '#f3f4f6',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
    marginTop: 8,
  },
  periodText: {
    fontSize: 8,
    fontWeight: 600,
    color: '#374151',
  },
  // Customer Info
  customerSection: {
    backgroundColor: '#f9fafb',
    padding: 16,
    borderRadius: 6,
    marginBottom: 24,
  },
  customerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  customerBlock: {
    flex: 1,
  },
  customerLabel: {
    fontSize: 7,
    fontWeight: 600,
    color: '#9ca3af',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
    marginBottom: 2,
  },
  customerValue: {
    fontSize: 10,
    color: '#1a1a1a',
  },
  // Summary Cards
  summarySection: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 11,
    fontWeight: 700,
    color: '#1a1a1a',
    marginBottom: 12,
    paddingBottom: 6,
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  summaryGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
  },
  summaryCard: {
    flex: 1,
    minWidth: 120,
    backgroundColor: '#f9fafb',
    padding: 12,
    borderRadius: 6,
    borderLeftWidth: 3,
    borderLeftColor: '#1a1a1a',
  },
  summaryLabel: {
    fontSize: 8,
    color: '#6b7280',
    marginBottom: 4,
  },
  summaryValue: {
    fontSize: 16,
    fontWeight: 700,
    color: '#1a1a1a',
  },
  summaryChange: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 4,
  },
  changePositive: {
    color: '#16a34a',
    fontSize: 8,
    fontWeight: 600,
  },
  changeNegative: {
    color: '#dc2626',
    fontSize: 8,
    fontWeight: 600,
  },
  changeLabel: {
    color: '#6b7280',
    fontSize: 7,
    marginLeft: 4,
  },
  // Balance Summary
  balanceSection: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 24,
    padding: 16,
    backgroundColor: '#1a1a1a',
    borderRadius: 6,
  },
  balanceBlock: {
    textAlign: 'center',
  },
  balanceLabel: {
    fontSize: 8,
    color: '#9ca3af',
    marginBottom: 4,
  },
  balanceValue: {
    fontSize: 18,
    fontWeight: 700,
    color: '#ffffff',
  },
  balanceArrow: {
    alignSelf: 'center',
    fontSize: 20,
    color: '#6b7280',
  },
  // Transactions Table
  transactionsSection: {
    marginBottom: 24,
  },
  table: {
    borderWidth: 1,
    borderColor: '#e5e7eb',
    borderRadius: 6,
    overflow: 'hidden',
  },
  tableHeader: {
    flexDirection: 'row',
    backgroundColor: '#1a1a1a',
    padding: 10,
  },
  tableHeaderText: {
    fontSize: 7,
    fontWeight: 600,
    color: '#ffffff',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  tableRow: {
    flexDirection: 'row',
    borderBottomWidth: 1,
    borderBottomColor: '#f3f4f6',
    padding: 10,
    alignItems: 'center',
  },
  tableRowAlt: {
    backgroundColor: '#fafafa',
  },
  colDate: { width: '12%' },
  colDescription: { flex: 1 },
  colReference: { width: '15%' },
  colType: { width: '12%' },
  colAmount: { width: '15%', textAlign: 'right' },
  colBalance: { width: '15%', textAlign: 'right' },
  cellText: {
    fontSize: 9,
    color: '#374151',
  },
  cellDescription: {
    fontSize: 9,
    color: '#1a1a1a',
    fontWeight: 600,
  },
  creditAmount: {
    color: '#16a34a',
    fontWeight: 600,
  },
  debitAmount: {
    color: '#dc2626',
    fontWeight: 600,
  },
  typeBadge: {
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 3,
    alignSelf: 'flex-start',
  },
  orderBadge: { backgroundColor: '#dbeafe' },
  paymentBadge: { backgroundColor: '#dcfce7' },
  refundBadge: { backgroundColor: '#fef3c7' },
  typeBadgeText: {
    fontSize: 7,
    fontWeight: 600,
    textTransform: 'uppercase',
  },
  orderText: { color: '#1e40af' },
  paymentText: { color: '#166534' },
  refundText: { color: '#92400e' },
  // Category Breakdown
  breakdownSection: {
    marginBottom: 24,
  },
  breakdownTable: {
    borderWidth: 1,
    borderColor: '#e5e7eb',
    borderRadius: 6,
    overflow: 'hidden',
  },
  breakdownRow: {
    flexDirection: 'row',
    padding: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#f3f4f6',
    alignItems: 'center',
  },
  breakdownCategory: {
    flex: 2,
    fontSize: 9,
    color: '#1a1a1a',
    fontWeight: 600,
  },
  breakdownBar: {
    flex: 3,
    height: 8,
    backgroundColor: '#e5e7eb',
    borderRadius: 4,
    marginHorizontal: 12,
    overflow: 'hidden',
  },
  breakdownBarFill: {
    height: '100%',
    backgroundColor: '#1a1a1a',
    borderRadius: 4,
  },
  breakdownAmount: {
    width: 80,
    textAlign: 'right',
    fontSize: 9,
    color: '#374151',
  },
  breakdownPercent: {
    width: 50,
    textAlign: 'right',
    fontSize: 9,
    color: '#6b7280',
  },
  // Notes
  notesSection: {
    backgroundColor: '#fffbeb',
    padding: 12,
    borderRadius: 6,
    borderLeftWidth: 3,
    borderLeftColor: '#f59e0b',
    marginBottom: 24,
  },
  notesTitle: {
    fontSize: 9,
    fontWeight: 600,
    color: '#92400e',
    marginBottom: 4,
  },
  notesText: {
    fontSize: 8,
    color: '#92400e',
    lineHeight: 1.5,
  },
  // Footer
  footer: {
    position: 'absolute',
    bottom: 30,
    left: 40,
    right: 40,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderTopWidth: 1,
    borderTopColor: '#e5e7eb',
    paddingTop: 16,
  },
  footerLeft: {
    fontSize: 7,
    color: '#9ca3af',
  },
  footerRight: {
    fontSize: 7,
    color: '#9ca3af',
  },
  pageNumber: {
    fontSize: 8,
    color: '#6b7280',
  },
})

const formatCurrency = (amount: number, currency: string = 'USD') => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
  }).format(amount)
}

const getTypeBadgeStyle = (type: Transaction['type']) => {
  switch (type) {
    case 'order':
      return { badge: styles.orderBadge, text: styles.orderText }
    case 'payment':
    case 'credit':
      return { badge: styles.paymentBadge, text: styles.paymentText }
    case 'refund':
      return { badge: styles.refundBadge, text: styles.refundText }
    default:
      return { badge: styles.orderBadge, text: styles.orderText }
  }
}

export function ReportStatementPDF({
  reportType = 'order-summary',
  reportTitle = 'Monthly Report',
  reportId = 'RPT-2024-001',
  generatedDate = new Date().toLocaleDateString(),
  reportPeriod = {
    startDate: '2024-01-01',
    endDate: '2024-01-31',
    label: 'January 2024',
  },
  company = {
    name: 'Your Company Name',
    address: '123 Business Street, San Francisco, CA 94107',
    email: 'reports@yourcompany.com',
    phone: '+1 (555) 123-4567',
  },
  customer,
  summary = [
    { label: 'Total Orders', value: 156, change: 12.5, changeLabel: 'vs last month' },
    { label: 'Total Revenue', value: '$24,500.00', change: 8.2, changeLabel: 'vs last month' },
    { label: 'Avg Order Value', value: '$157.05', change: -2.1, changeLabel: 'vs last month' },
    { label: 'Total Customers', value: 89, change: 15.0, changeLabel: 'vs last month' },
  ],
  transactions = [
    { date: '2024-01-15', description: 'Order #1234', reference: 'ORD-1234', type: 'order' as const, amount: -250.00, balance: 750.00 },
    { date: '2024-01-16', description: 'Payment Received', reference: 'PAY-5678', type: 'payment' as const, amount: 500.00, balance: 1250.00 },
    { date: '2024-01-18', description: 'Refund - Order #1230', reference: 'REF-9012', type: 'refund' as const, amount: 75.00, balance: 1325.00 },
  ],
  categoryBreakdown = [
    { category: 'Electronics', amount: 8500, percentage: 35, count: 45 },
    { category: 'Clothing', amount: 6200, percentage: 25, count: 62 },
    { category: 'Home & Garden', amount: 4800, percentage: 20, count: 28 },
    { category: 'Sports', amount: 3000, percentage: 12, count: 15 },
    { category: 'Other', amount: 2000, percentage: 8, count: 6 },
  ],
  openingBalance = 1000.00,
  closingBalance = 1325.00,
  notes,
  currency = 'USD',
}: ReportStatementPDFProps) {
  return (
    <Document>
      <Page size="A4" style={styles.page}>
        {/* Header */}
        <View style={styles.header}>
          <View style={styles.companyInfo}>
            <Text style={styles.companyName}>{company.name}</Text>
            <Text style={styles.companyDetails}>
              {company.address && `${company.address}\n`}
              {company.email && `${company.email}\n`}
              {company.phone && company.phone}
            </Text>
          </View>
          <View style={styles.reportInfo}>
            <Text style={styles.reportTitle}>{reportTitle}</Text>
            <Text style={styles.reportMeta}>Report ID: {reportId}</Text>
            <Text style={styles.reportMeta}>Generated: {generatedDate}</Text>
            <View style={styles.periodBadge}>
              <Text style={styles.periodText}>
                {reportPeriod.label || `${reportPeriod.startDate} - ${reportPeriod.endDate}`}
              </Text>
            </View>
          </View>
        </View>

        {/* Customer Info (if provided) */}
        {customer && (
          <View style={styles.customerSection}>
            <View style={styles.customerRow}>
              <View style={styles.customerBlock}>
                <Text style={styles.customerLabel}>Customer Name</Text>
                <Text style={styles.customerValue}>{customer.name}</Text>
              </View>
              <View style={styles.customerBlock}>
                <Text style={styles.customerLabel}>Email</Text>
                <Text style={styles.customerValue}>{customer.email}</Text>
              </View>
              {customer.accountId && (
                <View style={styles.customerBlock}>
                  <Text style={styles.customerLabel}>Account ID</Text>
                  <Text style={styles.customerValue}>{customer.accountId}</Text>
                </View>
              )}
              {customer.memberSince && (
                <View style={styles.customerBlock}>
                  <Text style={styles.customerLabel}>Member Since</Text>
                  <Text style={styles.customerValue}>{customer.memberSince}</Text>
                </View>
              )}
            </View>
          </View>
        )}

        {/* Summary Metrics */}
        <View style={styles.summarySection}>
          <Text style={styles.sectionTitle}>Summary</Text>
          <View style={styles.summaryGrid}>
            {summary.map((metric, index) => (
              <View key={index} style={styles.summaryCard}>
                <Text style={styles.summaryLabel}>{metric.label}</Text>
                <Text style={styles.summaryValue}>
                  {typeof metric.value === 'number' ? metric.value.toLocaleString() : metric.value}
                </Text>
                {metric.change !== undefined && (
                  <View style={styles.summaryChange}>
                    <Text style={metric.change >= 0 ? styles.changePositive : styles.changeNegative}>
                      {metric.change >= 0 ? '+' : ''}{metric.change}%
                    </Text>
                    {metric.changeLabel && (
                      <Text style={styles.changeLabel}>{metric.changeLabel}</Text>
                    )}
                  </View>
                )}
              </View>
            ))}
          </View>
        </View>

        {/* Balance Summary (for account statements) */}
        {reportType === 'account-statement' && openingBalance !== undefined && closingBalance !== undefined && (
          <View style={styles.balanceSection}>
            <View style={styles.balanceBlock}>
              <Text style={styles.balanceLabel}>Opening Balance</Text>
              <Text style={styles.balanceValue}>{formatCurrency(openingBalance, currency)}</Text>
            </View>
            <Text style={styles.balanceArrow}>→</Text>
            <View style={styles.balanceBlock}>
              <Text style={styles.balanceLabel}>Closing Balance</Text>
              <Text style={styles.balanceValue}>{formatCurrency(closingBalance, currency)}</Text>
            </View>
          </View>
        )}

        {/* Category Breakdown (for sales reports) */}
        {categoryBreakdown && categoryBreakdown.length > 0 && (
          <View style={styles.breakdownSection}>
            <Text style={styles.sectionTitle}>Category Breakdown</Text>
            <View style={styles.breakdownTable}>
              {categoryBreakdown.map((item, index) => (
                <View key={index} style={[styles.breakdownRow, index % 2 === 1 && styles.tableRowAlt]}>
                  <Text style={styles.breakdownCategory}>{item.category}</Text>
                  <View style={styles.breakdownBar}>
                    <View style={[styles.breakdownBarFill, { width: `${item.percentage}%` }]} />
                  </View>
                  <Text style={styles.breakdownAmount}>{formatCurrency(item.amount, currency)}</Text>
                  <Text style={styles.breakdownPercent}>{item.percentage}%</Text>
                </View>
              ))}
            </View>
          </View>
        )}

        {/* Transactions Table */}
        {transactions && transactions.length > 0 && (
          <View style={styles.transactionsSection}>
            <Text style={styles.sectionTitle}>
              {reportType === 'account-statement' ? 'Transaction History' : 'Recent Transactions'}
            </Text>
            <View style={styles.table}>
              {/* Table Header */}
              <View style={styles.tableHeader}>
                <Text style={[styles.tableHeaderText, styles.colDate]}>Date</Text>
                <Text style={[styles.tableHeaderText, styles.colDescription]}>Description</Text>
                <Text style={[styles.tableHeaderText, styles.colReference]}>Reference</Text>
                <Text style={[styles.tableHeaderText, styles.colType]}>Type</Text>
                <Text style={[styles.tableHeaderText, styles.colAmount]}>Amount</Text>
                {reportType === 'account-statement' && (
                  <Text style={[styles.tableHeaderText, styles.colBalance]}>Balance</Text>
                )}
              </View>

              {/* Table Rows */}
              {transactions.map((tx, index) => {
                const typeStyle = getTypeBadgeStyle(tx.type)
                return (
                  <View key={index} style={[styles.tableRow, index % 2 === 1 && styles.tableRowAlt]}>
                    <Text style={[styles.cellText, styles.colDate]}>{tx.date}</Text>
                    <Text style={[styles.cellDescription, styles.colDescription]}>{tx.description}</Text>
                    <Text style={[styles.cellText, styles.colReference]}>{tx.reference || '-'}</Text>
                    <View style={styles.colType}>
                      <View style={[styles.typeBadge, typeStyle.badge]}>
                        <Text style={[styles.typeBadgeText, typeStyle.text]}>
                          {tx.type}
                        </Text>
                      </View>
                    </View>
                    <Text style={[
                      styles.cellText, 
                      styles.colAmount,
                      tx.amount >= 0 ? styles.creditAmount : styles.debitAmount
                    ]}>
                      {tx.amount >= 0 ? '+' : ''}{formatCurrency(tx.amount, currency)}
                    </Text>
                    {reportType === 'account-statement' && tx.balance !== undefined && (
                      <Text style={[styles.cellText, styles.colBalance]}>
                        {formatCurrency(tx.balance, currency)}
                      </Text>
                    )}
                  </View>
                )
              })}
            </View>
          </View>
        )}

        {/* Notes */}
        {notes && (
          <View style={styles.notesSection}>
            <Text style={styles.notesTitle}>Notes</Text>
            <Text style={styles.notesText}>{notes}</Text>
          </View>
        )}

        {/* Footer */}
        <View style={styles.footer}>
          <Text style={styles.footerLeft}>
            {company.name} • Confidential
          </Text>
          <Text style={styles.pageNumber}>Page 1 of 1</Text>
          <Text style={styles.footerRight}>
            Generated on {generatedDate}
          </Text>
        </View>
      </Page>
    </Document>
  )
}

export default ReportStatementPDF
