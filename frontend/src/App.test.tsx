import { render, screen } from '@testing-library/react';
import App from './App';

// Mock scrollIntoView
window.HTMLElement.prototype.scrollIntoView = vi.fn();

test('renders app header', () => {
  render(<App />);
  const headerElement = screen.getByAltText(/logo/i);
  expect(headerElement).toBeInTheDocument();
});
