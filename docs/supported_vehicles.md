# Supported Vehicles

## SAAB 9-3 (YS3F, 2003–2011)

| Engine       | ECM Part No.   | Protocol   | Bus   | Notes                          |
|--------------|----------------|------------|-------|--------------------------------|
| B207E/R/L/S  | 55566062 series| ISO15765   | HS-CAN| Trifonic / Hirsch tunable      |
| B284E/L/R    | 55566062 series| ISO15765   | HS-CAN| V6 Turbo                       |
| Z18XER/XNH   | 55568310 series| ISO15765   | HS-CAN| NA diesel option               |
| Z19DTH/DTJ   | 55567480 series| ISO15765   | HS-CAN| 1.9 CDTI diesel                |

## SAAB 9-5 (YS3E, 1998–2005)

| Engine       | ECM            | Protocol   | Bus      | Notes                        |
|--------------|----------------|------------|----------|------------------------------|
| B235E/R/L    | 09188115 series| KWP2000    | K-line   | Pre-CAN; use ISO14230        |
| B308E        | 09145204       | KWP2000    | K-line   | V6 petrol                    |
| D308L        | 09171280       | KWP2000    | K-line   | 3.0 TiD diesel               |

## SAAB 9-5 (YS3G, 2010–2011)

| Engine       | ECM Part No.   | Protocol   | Bus   | Notes                          |
|--------------|----------------|------------|-------|--------------------------------|
| B284E/L      | 12622693 series| ISO15765   | HS-CAN| Shares platform with Opel Insignia |
| A28NET       | 12672484 series| ISO15765   | HS-CAN| 325 hp Aero variant            |

## Related GM platforms (partial support)

The following GM platforms share ECUs and protocols with the SAAB models above.
Basic DTC read/clear and live data work; SPS calibrations are vehicle-specific.

- Opel/Vauxhall Astra H, Vectra C, Zafira B, Signum
- Opel/Vauxhall Insignia A (shares YS3G architecture)
- Chevrolet Cobalt, HHR (US market, same ECM family as 9-3 II)

## Protocol quick-reference

| Year range  | Protocol     | Interface setting       |
|-------------|--------------|-------------------------|
| 1998–2002   | KWP2000      | `--protocol ISO14230`   |
| 2003–2011   | UDS/ISO15765 | `--protocol ISO15765`   |

## Tested configurations

| Vehicle               | Interface          | OS       | Result |
|-----------------------|--------------------|----------|--------|
| 9-3 2006 B207R        | GM MDI (J2534)     | Windows  | ✓      |
| 9-3 2008 Z19DTH       | PEAK PCAN-USB      | Linux    | ✓      |
| 9-5 2002 B235R        | MongoosePro GM II  | Windows  | ✓      |
| 9-5 2011 B284L        | GM MDI 2           | Windows  | ✓      |
| Astra H 2005 Z18XER   | Tactrix Openport   | Windows  | ✓      |
