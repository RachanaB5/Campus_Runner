/**
 * Password Reset Email Template
 * Usage: Forgot password flow, security-triggered password resets
 * 
 * Dependencies: @react-email/components
 * 
 * Props:
 * - customerName: string - Customer's display name
 * - resetUrl: string - Password reset link (with token)
 * - expiryHours: number - How long the link is valid
 * - ipAddress: string - IP that requested the reset
 * - userAgent: string - Browser/device info
 * - companyName: string - Your company name
 * - supportEmail: string - Support email address
 */

import {
  Body,
  Button,
  Container,
  Head,
  Heading,
  Hr,
  Html,
  Img,
  Link,
  Preview,
  Section,
  Text,
} from '@react-email/components'

interface PasswordResetEmailProps {
  customerName: string
  resetUrl: string
  expiryHours: number
  ipAddress?: string
  userAgent?: string
  requestTime?: string
  companyName: string
  companyLogo?: string
  supportEmail: string
}

export function PasswordResetEmail({
  customerName = 'Customer',
  resetUrl = 'https://yourstore.com/reset-password?token=xxx',
  expiryHours = 24,
  ipAddress = '192.168.1.1',
  userAgent = 'Chrome on Windows',
  requestTime = new Date().toLocaleString(),
  companyName = 'Your Store',
  companyLogo,
  supportEmail = 'support@yourstore.com',
}: PasswordResetEmailProps) {
  return (
    <Html>
      <Head />
      <Preview>Reset your {companyName} password</Preview>
      <Body style={main}>
        <Container style={container}>
          {/* Header */}
          <Section style={header}>
            {companyLogo ? (
              <Img src={companyLogo} width="120" height="40" alt={companyName} />
            ) : (
              <Text style={logoText}>{companyName}</Text>
            )}
          </Section>

          {/* Main Content */}
          <Section style={content}>
            <Section style={iconContainer}>
              <Text style={iconText}>🔐</Text>
            </Section>

            <Heading style={heading}>Reset Your Password</Heading>
            
            <Text style={paragraph}>Hi {customerName},</Text>
            
            <Text style={paragraph}>
              We received a request to reset the password for your {companyName} account. 
              Click the button below to create a new password:
            </Text>

            {/* CTA Button */}
            <Section style={ctaContainer}>
              <Button style={ctaButton} href={resetUrl}>
                Reset Password
              </Button>
            </Section>

            <Text style={linkFallback}>
              Or copy and paste this URL into your browser:{'\n'}
              <Link href={resetUrl} style={urlLink}>
                {resetUrl}
              </Link>
            </Text>

            <Text style={expiryText}>
              This link will expire in {expiryHours} hours.
            </Text>

            <Hr style={divider} />

            {/* Request Details */}
            <Section style={detailsBox}>
              <Text style={detailsTitle}>Request Details</Text>
              <Text style={detailsText}>
                <strong>Time:</strong> {requestTime}{'\n'}
                <strong>IP Address:</strong> {ipAddress}{'\n'}
                <strong>Device:</strong> {userAgent}
              </Text>
            </Section>

            {/* Security Warning */}
            <Section style={warningBox}>
              <Text style={warningTitle}>Didn&apos;t request this?</Text>
              <Text style={warningText}>
                If you didn&apos;t request a password reset, please ignore this email 
                or <Link href={`mailto:${supportEmail}`} style={warningLink}>contact our security team</Link> immediately. 
                Your password will remain unchanged.
              </Text>
            </Section>

            {/* Security Tips */}
            <Section style={tipsBox}>
              <Text style={tipsTitle}>Password Tips:</Text>
              <Text style={tipsText}>
                • Use at least 12 characters{'\n'}
                • Include uppercase and lowercase letters{'\n'}
                • Add numbers and special characters{'\n'}
                • Avoid using personal information{'\n'}
                • Don&apos;t reuse passwords from other sites
              </Text>
            </Section>
          </Section>

          {/* Footer */}
          <Section style={footer}>
            <Text style={footerText}>
              This is an automated security email from {companyName}.
            </Text>
            <Text style={footerText}>
              If you have questions, contact us at{' '}
              <Link href={`mailto:${supportEmail}`} style={footerLink}>
                {supportEmail}
              </Link>
            </Text>
            <Text style={footerText}>
              © {new Date().getFullYear()} {companyName}. All rights reserved.
            </Text>
          </Section>
        </Container>
      </Body>
    </Html>
  )
}

// Styles
const main = {
  backgroundColor: '#f6f9fc',
  fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Ubuntu, sans-serif',
}

const container = {
  backgroundColor: '#ffffff',
  margin: '0 auto',
  maxWidth: '600px',
}

const header = {
  padding: '32px 48px',
  borderBottom: '1px solid #e6ebf1',
}

const logoText = {
  fontSize: '24px',
  fontWeight: '700',
  color: '#1a1a1a',
  margin: '0',
}

const content = {
  padding: '32px 48px',
}

const iconContainer = {
  textAlign: 'center' as const,
  marginBottom: '16px',
}

const iconText = {
  fontSize: '48px',
  margin: '0',
}

const heading = {
  color: '#1a1a1a',
  fontSize: '24px',
  fontWeight: '600',
  textAlign: 'center' as const,
  margin: '0 0 24px',
}

const paragraph = {
  color: '#525f7f',
  fontSize: '16px',
  lineHeight: '24px',
  margin: '0 0 16px',
}

const ctaContainer = {
  textAlign: 'center' as const,
  margin: '32px 0',
}

const ctaButton = {
  backgroundColor: '#dc2626',
  borderRadius: '8px',
  color: '#ffffff',
  fontSize: '16px',
  fontWeight: '600',
  padding: '14px 32px',
  textDecoration: 'none',
}

const linkFallback = {
  color: '#6b7280',
  fontSize: '13px',
  lineHeight: '20px',
  textAlign: 'center' as const,
  margin: '16px 0',
  wordBreak: 'break-all' as const,
}

const urlLink = {
  color: '#556cd6',
  textDecoration: 'underline',
}

const expiryText = {
  color: '#8898aa',
  fontSize: '14px',
  textAlign: 'center' as const,
  margin: '16px 0 0',
}

const divider = {
  borderColor: '#e6ebf1',
  margin: '32px 0',
}

const detailsBox = {
  backgroundColor: '#f9fafb',
  borderRadius: '8px',
  padding: '16px',
  marginBottom: '16px',
}

const detailsTitle = {
  color: '#374151',
  fontSize: '14px',
  fontWeight: '600',
  margin: '0 0 8px',
}

const detailsText = {
  color: '#6b7280',
  fontSize: '13px',
  lineHeight: '22px',
  margin: '0',
  whiteSpace: 'pre-line' as const,
}

const warningBox = {
  backgroundColor: '#fef2f2',
  borderRadius: '8px',
  padding: '16px',
  marginBottom: '16px',
  borderLeft: '4px solid #dc2626',
}

const warningTitle = {
  color: '#991b1b',
  fontSize: '14px',
  fontWeight: '600',
  margin: '0 0 8px',
}

const warningText = {
  color: '#991b1b',
  fontSize: '13px',
  lineHeight: '20px',
  margin: '0',
}

const warningLink = {
  color: '#991b1b',
  fontWeight: '600',
  textDecoration: 'underline',
}

const tipsBox = {
  backgroundColor: '#f0fdf4',
  borderRadius: '8px',
  padding: '16px',
}

const tipsTitle = {
  color: '#166534',
  fontSize: '14px',
  fontWeight: '600',
  margin: '0 0 8px',
}

const tipsText = {
  color: '#166534',
  fontSize: '13px',
  lineHeight: '22px',
  margin: '0',
  whiteSpace: 'pre-line' as const,
}

const footer = {
  padding: '32px 48px',
  borderTop: '1px solid #e6ebf1',
  textAlign: 'center' as const,
}

const footerText = {
  color: '#8898aa',
  fontSize: '12px',
  margin: '0 0 8px',
}

const footerLink = {
  color: '#556cd6',
  textDecoration: 'underline',
}

export default PasswordResetEmail
