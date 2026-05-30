import userEvent from '@testing-library/user-event'
import { render, screen } from '@testing-library/vue'

import JsonViewer from '@/components/dashboard/JsonViewer.vue'

describe('JsonViewer', () => {
  it('renders formatted nested JSON and supports collapse', async () => {
    const user = userEvent.setup()
    render(JsonViewer, {
      props: {
        label: 'Payload Original',
        value: { message: 'hello', nested: { active: true }, values: [1, 2] }
      }
    })

    expect(screen.getByText('Payload Original')).toBeInTheDocument()
    expect(screen.getByText('"message":')).toBeInTheDocument()
    expect(screen.getByText('"nested":')).toBeInTheDocument()

    await user.click(screen.getAllByRole('button', { name: 'Recolher JSON' })[0])
    expect(screen.getByText(/3 items/)).toBeInTheDocument()
  })

  it('renders null values', () => {
    render(JsonViewer, {
      props: {
        label: 'Resposta',
        value: null
      }
    })

    expect(screen.getByText('null')).toBeInTheDocument()
  })
})
