// Reference repair cost ranges (USD) — typical industry figures used as a sanity prior.
// Inlined into the system prompt so Claude can ground its estimate while still
// adjusting for vehicle tier and severity.
//
// Source: aggregated from RepairPal, AAA, and consumer auto-repair guides.
// These are intentionally rough — production would replace with Mitchell/CCC/Audatex.

export const DAMAGE_PRIORS = `
TYPICAL REPAIR COST RANGES (USD), by vehicle tier:

Bumper dent, paintless repair:
  Economy: $400-1,200    Midrange: $800-2,500     Luxury: $1,500-5,000
Bumper replacement (parts + paint + labor):
  Economy: $800-2,000    Midrange: $1,500-4,000   Luxury: $3,000-8,000
Quarter panel repair (dent + paint):
  Economy: $500-1,500    Midrange: $1,000-3,000   Luxury: $2,000-6,000
Quarter panel replacement:
  Economy: $1,500-3,500  Midrange: $2,500-6,000   Luxury: $5,000-12,000
Door repair (dent + paint):
  Economy: $400-1,200    Midrange: $700-2,200     Luxury: $1,500-4,500
Door replacement:
  Economy: $1,000-2,500  Midrange: $1,800-4,500   Luxury: $3,500-9,000
Headlight assembly replacement:
  Economy: $300-700      Midrange: $600-1,500     Luxury: $1,200-3,000
Taillight replacement:
  Economy: $200-500      Midrange: $400-1,000     Luxury: $800-2,000
Windshield replacement:
  Economy: $200-500      Midrange: $400-900       Luxury: $800-2,000
Side mirror replacement:
  Economy: $150-450      Midrange: $300-800       Luxury: $700-1,800
Hood repair (dent + paint):
  Economy: $500-1,500    Midrange: $900-2,500     Luxury: $2,000-5,500
Hood replacement:
  Economy: $1,200-2,800  Midrange: $2,000-4,500   Luxury: $4,000-9,000
Scratch repair (single panel, light):
  Economy: $150-500      Midrange: $300-900       Luxury: $600-1,800
Multi-panel scratch / scuff:
  Economy: $400-1,200    Midrange: $800-2,500     Luxury: $1,800-5,000

Vehicle-tier guidance:
- Economy: Honda Civic, Toyota Corolla, Hyundai Elantra, Nissan Sentra, Kia Forte, Chevy Cruze
- Midrange: Toyota Camry, Honda Accord, Mazda CX-5, Subaru Outback, Hyundai Sonata, most crossovers
- Luxury: BMW, Mercedes, Audi, Lexus, Acura, Cadillac, Tesla, Porsche, Range Rover, Volvo

Severity multipliers to apply on top of the ranges above:
- Minor (single panel, no structural concern): use the lower half of the range
- Moderate (multiple panels OR potential alignment work): use the upper half
- Severe (visible structural damage, airbag deployment, frame concerns): typically exceeds these ranges; flag for adjuster review and provide a wide range
`;
