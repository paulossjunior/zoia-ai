import { render, screen } from '@testing-library/vue'

import IndicatorsGrid from '@/components/dashboard/IndicatorsGrid.vue'

import { indicatorsFixture } from './fixtures'

describe('IndicatorsGrid', () => {
  it('renders all operational counters', () => {
    render(IndicatorsGrid, {
      props: {
        indicators: indicatorsFixture
      }
    })

    expect(screen.getByText('Total de comandos')).toBeInTheDocument()
    expect(screen.getByText('Total em fila')).toBeInTheDocument()
    expect(screen.getByText('Total em processamento')).toBeInTheDocument()
    expect(screen.getByText('Total concluídos')).toBeInTheDocument()
    expect(screen.getByText('Total com falha')).toBeInTheDocument()
    expect(screen.getByText('Total callback not_required')).toBeInTheDocument()
    expect(screen.getByText('Total callback pending')).toBeInTheDocument()
    expect(screen.getByText('Total callback sent')).toBeInTheDocument()
    expect(screen.getByText('Total callback failed')).toBeInTheDocument()
  })
})
