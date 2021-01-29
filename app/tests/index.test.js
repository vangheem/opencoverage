import { render, screen } from '@testing-library/react'
import App from '../pages/index'

describe('App', () => {
  it('renders without crashing', () => {
    const { container } = render(<App />)
    const h1 = container.querySelector('h1')
    expect(h1.textContent).toEqual(
      'Open coverage: Open source coverage reporting'
    )
  })
})
