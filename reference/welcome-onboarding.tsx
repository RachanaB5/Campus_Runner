/**
 * Welcome/Onboarding Email Template
 * Usage: New user registration, account creation confirmation
 * 
 * Dependencies: @react-email/components
 * 
 * Props:
 * - customerName: string - Customer's display name
 * - email: string - Customer's email
 * - companyName: string - Your company name
 * - dashboardUrl: string - Link to user dashboard
 * - features: Array<{title, description}> - Key features to highlight
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

interface Feature {
  icon: string
  title: string
  description: string
}

interface WelcomeEmailProps {
  customerName: string
  email: string
  companyName: string
  companyLogo?: string
  dashboardUrl: string
  features?: Feature[]
  supportEmail: string
  socialLinks?: {
    twitter?: string
    facebook?: string
    instagram?: string
  }
}

const defaultFeatures: Feature[] = [
  {
    icon: '🛍️',
    title: 'Browse Products',
    description: 'Explore thousands of products across categories',
  },
  {
    icon: '🚚',
    title: 'Fast Shipping',
    description: 'Free shipping on orders over $50',
  },
  {
    icon: '💳',
    title: 'Secure Payments',
    description: 'Multiple payment options with buyer protection',
  },
  {
    icon: '🎁',
    title: 'Rewards Program',
    description: 'Earn points on every purchase',
  },
]

export function WelcomeEmail({
  customerName = 'Customer',
  email = 'customer@example.com',
  companyName = 'Your Store',
  companyLogo,
  dashboardUrl = 'https://yourstore.com/dashboard',
  features = defaultFeatures,
  supportEmail = 'support@yourstore.com',
  socialLinks,
}: WelcomeEmailProps) {
  return (
    <Html>
      <Head />
      <Preview>Welcome to {companyName} - Let&apos;s get started!</Preview>
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

          {/* Hero Section */}
          <Section style={heroSection}>
            <Heading style={heroHeading}>Welcome to {companyName}!</Heading>
            <Text style={heroText}>
              We&apos;re thrilled to have you join our community
            </Text>
          </Section>

          {/* Main Content */}
          <Section style={content}>
            <Text style={paragraph}>Hi {customerName},</Text>
            
            <Text style={paragraph}>
              Thank you for creating an account with us! Your account has been 
              successfully set up with the email address <strong>{email}</strong>.
            </Text>

            <Text style={paragraph}>
              You now have access to exclusive deals, order tracking, wishlists, 
              and much more. Here&apos;s what you can do:
            </Text>

            {/* Features Grid */}
            <Section style={featuresContainer}>
              {features.map((feature, index) => (
                <Section key={index} style={featureBox}>
                  <Text style={featureIcon}>{feature.icon}</Text>
                  <Text style={featureTitle}>{feature.title}</Text>
                  <Text style={featureDescription}>{feature.description}</Text>
                </Section>
              ))}
            </Section>

            {/* CTA Button */}
            <Section style={ctaContainer}>
              <Button style={ctaButton} href={dashboardUrl}>
                Start Shopping
              </Button>
            </Section>

            <Hr style={divider} />

            {/* Quick Links */}
            <Section style={quickLinksSection}>
              <Text style={quickLinksTitle}>Quick Links</Text>
              <Text style={quickLinksText}>
                <Link href={`${dashboardUrl}/profile`} style={link}>Complete Your Profile</Link>
                {' • '}
                <Link href={`${dashboardUrl}/orders`} style={link}>Track Orders</Link>
                {' • '}
                <Link href={`${dashboardUrl}/wishlist`} style={link}>Wishlist</Link>
                {' • '}
                <Link href={`${dashboardUrl}/settings`} style={link}>Settings</Link>
              </Text>
            </Section>

            {/* Support Box */}
            <Section style={supportBox}>
              <Text style={supportTitle}>Need Help?</Text>
              <Text style={supportText}>
                Our customer support team is here to help you 24/7. Reach out 
                anytime at{' '}
                <Link href={`mailto:${supportEmail}`} style={link}>
                  {supportEmail}
                </Link>
              </Text>
            </Section>
          </Section>

          {/* Footer */}
          <Section style={footer}>
            {socialLinks && (
              <Section style={socialSection}>
                {socialLinks.twitter && (
                  <Link href={socialLinks.twitter} style={socialLink}>Twitter</Link>
                )}
                {socialLinks.facebook && (
                  <Link href={socialLinks.facebook} style={socialLink}>Facebook</Link>
                )}
                {socialLinks.instagram && (
                  <Link href={socialLinks.instagram} style={socialLink}>Instagram</Link>
                )}
              </Section>
            )}
            <Text style={footerText}>
              © {new Date().getFullYear()} {companyName}. All rights reserved.
            </Text>
            <Text style={footerLinks}>
              <Link href="#" style={footerLink}>Privacy Policy</Link>
              {' • '}
              <Link href="#" style={footerLink}>Terms of Service</Link>
              {' • '}
              <Link href="#" style={footerLink}>Unsubscribe</Link>
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

const heroSection = {
  backgroundColor: '#1a1a1a',
  padding: '48px',
  textAlign: 'center' as const,
}

const heroHeading = {
  color: '#ffffff',
  fontSize: '28px',
  fontWeight: '700',
  margin: '0 0 8px',
}

const heroText = {
  color: '#a3a3a3',
  fontSize: '16px',
  margin: '0',
}

const content = {
  padding: '32px 48px',
}

const paragraph = {
  color: '#525f7f',
  fontSize: '16px',
  lineHeight: '24px',
  margin: '0 0 16px',
}

const featuresContainer = {
  margin: '32px 0',
}

const featureBox = {
  backgroundColor: '#f9fafb',
  borderRadius: '8px',
  padding: '16px',
  marginBottom: '12px',
}

const featureIcon = {
  fontSize: '24px',
  margin: '0 0 8px',
}

const featureTitle = {
  color: '#1a1a1a',
  fontSize: '16px',
  fontWeight: '600',
  margin: '0 0 4px',
}

const featureDescription = {
  color: '#6b7280',
  fontSize: '14px',
  margin: '0',
}

const ctaContainer = {
  textAlign: 'center' as const,
  margin: '32px 0',
}

const ctaButton = {
  backgroundColor: '#1a1a1a',
  borderRadius: '8px',
  color: '#ffffff',
  fontSize: '16px',
  fontWeight: '600',
  padding: '14px 32px',
  textDecoration: 'none',
}

const divider = {
  borderColor: '#e6ebf1',
  margin: '32px 0',
}

const quickLinksSection = {
  textAlign: 'center' as const,
  margin: '24px 0',
}

const quickLinksTitle = {
  color: '#1a1a1a',
  fontSize: '14px',
  fontWeight: '600',
  margin: '0 0 8px',
}

const quickLinksText = {
  color: '#6b7280',
  fontSize: '14px',
  margin: '0',
}

const link = {
  color: '#556cd6',
  textDecoration: 'underline',
}

const supportBox = {
  backgroundColor: '#eff6ff',
  borderRadius: '8px',
  padding: '20px',
  marginTop: '24px',
}

const supportTitle = {
  color: '#1e40af',
  fontSize: '16px',
  fontWeight: '600',
  margin: '0 0 8px',
}

const supportText = {
  color: '#1e40af',
  fontSize: '14px',
  lineHeight: '20px',
  margin: '0',
}

const footer = {
  padding: '32px 48px',
  borderTop: '1px solid #e6ebf1',
  textAlign: 'center' as const,
}

const socialSection = {
  marginBottom: '16px',
}

const socialLink = {
  color: '#6b7280',
  fontSize: '14px',
  marginRight: '16px',
  textDecoration: 'none',
}

const footerText = {
  color: '#8898aa',
  fontSize: '12px',
  margin: '0 0 8px',
}

const footerLinks = {
  color: '#8898aa',
  fontSize: '12px',
  margin: '0',
}

const footerLink = {
  color: '#8898aa',
  textDecoration: 'underline',
}

export default WelcomeEmail
