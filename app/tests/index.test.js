import { render, screen } from '@testing-library/react'
import App from '../pages/index'
import Docs from '../pages/docs/index'
import IntegrationDocs from '../pages/docs/integration/index'
import HostingDocs from '../pages/docs/hosting/index'

describe('App', () => {
  it('renders without crashing', () => {
    const { container } = render(<App />)
    const h1 = container.querySelector('h1')
    expect(h1.textContent).toContain('Open Coverage:')
  })

  it('docs renders without crashing', () => {
    const { container } = render(<Docs />)
    const h1 = container.querySelector('h1')
    expect(h1.textContent).toContain('Open Coverage Documentation')
  })

  it('integration docs renders without crashing', () => {
    const { container } = render(<IntegrationDocs />)
    const h1 = container.querySelector('h1')
    expect(h1.textContent).toContain('Open Coverage Documentation')
  })

  it('integration docs renders without crashing', () => {
    const { container } = render(<HostingDocs />)
    const h1 = container.querySelector('h1')
    expect(h1.textContent).toContain('Open Coverage Documentation')
  })
})
