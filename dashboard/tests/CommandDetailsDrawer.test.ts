import { render, screen } from '@testing-library/vue'

import CommandDetailsDrawer from '@/components/dashboard/CommandDetailsDrawer.vue'

import { commandDetailFixture, failingCommandDetailFixture } from './fixtures'

describe('CommandDetailsDrawer', () => {
  it('renders identification, processing, callback, payload, response, and error sections', () => {
    render(CommandDetailsDrawer, {
      props: {
        command: failingCommandDetailFixture,
        loading: false
      }
    })

    expect(screen.getByText(failingCommandDetailFixture.command_id)).toBeInTheDocument()
    expect(screen.getByText('SEND_EMAIL')).toBeInTheDocument()
    expect(screen.getByText('Callback Error Message')).toBeInTheDocument()
    expect(screen.getByText('timeout')).toBeInTheDocument()
    expect(screen.getByText('Payload Original')).toBeInTheDocument()
    expect(screen.getByText('Resposta')).toBeInTheDocument()
    expect(screen.getByText('handler failed')).toBeInTheDocument()
  })

  it('renders loading state', () => {
    render(CommandDetailsDrawer, {
      props: {
        command: commandDetailFixture,
        loading: true
      }
    })

    expect(screen.getByRole('status')).toHaveTextContent('Carregando detalhes...')
  })
})
