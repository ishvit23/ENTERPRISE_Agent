import React from 'react';
import { render, screen } from '@testing-library/react';
import KnowledgeBase from '../components/KnowledgeBase';

jest.mock('../services/api', () => ({
  fetchDocuments: jest.fn(() => Promise.resolve({ documents: [] })),
}));

describe('KnowledgeBase', () => {
  it('renders loading and empty state', async () => {
    render(<KnowledgeBase />);
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
    // Wait for empty state
    const empty = await screen.findByText(/no documents found/i);
    expect(empty).toBeInTheDocument();
  });
});
