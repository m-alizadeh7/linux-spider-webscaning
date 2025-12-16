# Security Policy

## Supported Versions

Currently supported versions with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security issue, please follow these steps:

### 1. **DO NOT** Open a Public Issue

Please do not report security vulnerabilities through public GitHub issues.

### 2. Report Privately

Send an email to the maintainers with:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### 3. Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Timeline**: Depends on severity
  - Critical: Within 7 days
  - High: Within 30 days
  - Medium: Within 90 days
  - Low: Next release cycle

### 4. Disclosure Policy

- We will acknowledge your report within 48 hours
- We will provide a detailed response with next steps within 7 days
- We will notify you when the vulnerability is fixed
- We will credit you in the security advisory (unless you prefer to remain anonymous)

## Security Best Practices

When using this tool:

1. **Authorization**: Always obtain proper authorization before scanning any website
2. **Rate Limiting**: Be respectful of target servers and avoid aggressive scanning
3. **API Keys**: Never commit API keys or credentials to the repository
4. **Updates**: Keep the tool and its dependencies up to date
5. **Debug Logs**: Be cautious when sharing debug logs as they may contain sensitive information

## Known Security Considerations

- This tool makes HTTP/HTTPS requests to target websites
- Some scanning modules may trigger security alerts on target systems
- Debug logs may contain URLs, headers, and response data
- Always review generated reports before sharing

## Dependencies

We regularly monitor and update dependencies for security vulnerabilities. You can check for updates:

```bash
pip list --outdated
```

## Responsible Disclosure

We believe in responsible disclosure and will work with security researchers to:
- Understand and reproduce the issue
- Develop and test a fix
- Release a patch
- Publicly disclose the vulnerability (after a fix is available)

Thank you for helping keep Linux Spider and its users safe!
