/**
 * OTP/Verification Email Template
 * Usage: Email verification, 2FA codes, phone verification
 * 
 * Dependencies: @react-email/components
 * 
 * Props:
 * - customerName: string - Customer's display name
 * - otpCode: string - The OTP code (usually 6 digits)
 * - expiryMinutes: number - How long the code is valid
 * - actionType: 'verify-email' | 'login' | 'password-reset' | 'transaction'
 * - companyName: string - Your company name
 * - supportEmail: string - Support email address
 */

import {
  Body,
  Container,
  Head,
  Heading,
  Html,
  Img,
  Link,
  Preview,
  Section,
  Text,
} from '@react-email/components'

interface OTPVerificationEmailProps {
  customerName: string
  otpCode: string
  expiryMinutes: number
  actionType: 'verify-email' | 'login' | 'password-reset' | 'transaction'
  companyName: string
  companyLogo?: string
  supportEmail: string
}

const actionMessages = {
  'verify-email': 'verify your email address',
  'login': 'complete your login',
  'password-reset': 'reset your password',
  'transaction': 'confirm your transaction',
}

export function OTPVerificationEmail({
  customerName = 'Customer',
  otpCode = '123456',
  expiryMinutes = 10,
  actionType = 'verify-email',
  companyName = 'Your Store',
  companyLogo,
  supportEmail = 'support@yourstore.com',
}: OTPVerificationEmailProps) {
  return (
    <Html>
      <Head />
      <Preview>Your verification code is {otpCode}</Preview>
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
            <Heading style={heading}>Verification Code</Heading>
            
            <Text style={paragraph}>Hi {customerName},</Text>
            
            <Text style={paragraph}>
              Use the following code to {actionMessages[actionType]}:
            </Text>

            {/* OTP Code Box */}
            <Section style={codeContainer}>
              <Text style={codeText}>{otpCode}</Text>
            </Section>

            <Text style={expiryText}>
              This code expires in {expiryMinutes} minutes.
            </Text>

            <Text style={paragraph}>
              If you didn&apos;t request this code, please ignore this email or contact 
              our support team if you have concerns.
            </Text>

            {/* Security Notice */}
            <Section style={securityBox}>
              <Text style={securityTitle}>Security Tips:</Text>
              <Text style={securityText}>
                • Never share this code with anyone{'\n'}
                • {companyName} will never ask for your code via phone{'\n'}
                • This code is for one-time use only
              </Text>
            </Section>
          </Section>

          {/* Footer */}
          <Section style={footer}>
            <Text style={footerText}>
              Need help? Contact us at{' '}
              <Link href={`mailto:${supportEmail}`} style={link}>
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
  padding: '20px 0 48px',
  marginBottom: '64px',
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

const heading = {
  color: '#1a1a1a',
  fontSize: '24px',
  fontWeight: '600',
  lineHeight: '1.3',
  margin: '0 0 24px',
}

const paragraph = {
  color: '#525f7f',
  fontSize: '16px',
  lineHeight: '24px',
  margin: '0 0 16px',
}

const codeContainer = {
  backgroundColor: '#f4f4f5',
  borderRadius: '8px',
  padding: '24px',
  margin: '24px 0',
  textAlign: 'center' as const,
}

const codeText = {
  color: '#1a1a1a',
  fontSize: '36px',
  fontWeight: '700',
  letterSpacing: '8px',
  margin: '0',
  fontFamily: 'monospace',
}

const expiryText = {
  color: '#8898aa',
  fontSize: '14px',
  textAlign: 'center' as const,
  margin: '0 0 24px',
}

const securityBox = {
  backgroundColor: '#fef3c7',
  borderRadius: '8px',
  padding: '16px',
  marginTop: '24px',
}

const securityTitle = {
  color: '#92400e',
  fontSize: '14px',
  fontWeight: '600',
  margin: '0 0 8px',
}

const securityText = {
  color: '#92400e',
  fontSize: '13px',
  lineHeight: '20px',
  margin: '0',
  whiteSpace: 'pre-line' as const,
}

const footer = {
  padding: '32px 48px',
  borderTop: '1px solid #e6ebf1',
}

const footerText = {
  color: '#8898aa',
  fontSize: '12px',
  lineHeight: '16px',
  margin: '0 0 8px',
}

const link = {
  color: '#556cd6',
  textDecoration: 'underline',
}

export default OTPVerificationEmail
