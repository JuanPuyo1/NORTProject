# NORT Phase 1 Blueprint Prompts

## How to use this document

1. Paste the primary prompt into [Blueprint](https://www.blueprint.io).
2. Do not purchase parts or connect the result to a person yet.
3. Export or save Blueprint's INFO, BOM, WIRING, MECH, and INSTRUCTIONS outputs.
4. Evaluate every output using `04-engineering-review-and-tests.md`.
5. Use the iteration prompt after listing concrete problems found in the first result.

Blueprint is being used to create a concept-level prototype plan. Its output is not a substitute for electrical, biomedical, battery, RF, mechanical, or regulatory review.

## Primary copy-paste prompt

```text
Project name: NORT P1 — Single-Pod EEG+sEMG Signal-Quality Wearable

Design a buildable, module-based research prototype for acquiring stable biopotential signals from one temple/behind-ear area. This is an acquisition and form-factor experiment only. It must not decode words, inner speech, thoughts, or medical conditions. It must not apply stimulation. It must not be presented as a medical-grade, clinically safe, diagnostic, therapeutic, or ALS-ready device.

PRIMARY OBJECTIVE

Create one reusable battery-powered electronics pod connected to one replaceable flexible adhesive electrode tail. The pod records local EEG/EOG-mixed biopotentials, one dedicated bipolar temporalis/jaw sEMG channel, and 6-axis motion data. It streams complete timestamped raw data to a phone or computer over Bluetooth Low Energy and buffers data during radio interruptions.

The first build must prefer purchasable modules, evaluation boards, and certified BLE radio modules instead of a custom PCB. It may be larger than the final product. Do not draw a ring-sized or invisible wearable if the selected modules do not physically fit. Report realistic assembled dimensions, mass, current consumption, and battery runtime.

ELECTRODE TAIL AND MONTAGE

Use a replaceable adhesive tail with six pre-gelled Ag/AgCl contacts on hairless skin:

- E1: anterior temple, local biopotential sensing.
- E2: posterior temple or upper preauricular area, local biopotential sensing.
- E3: mastoid or hairless area behind the ear, shared reference.
- E4: lower behind-ear bias/ground return, only through a reviewed current-limited bias network.
- E5 and E6: a bipolar pair over lower temporalis or upper jaw for a dedicated sEMG witness channel.

Initial channels:

- CH1 = E1 relative to E3.
- CH2 = E2 relative to E3.
- CH3 = E5 relative to E6, dedicated sEMG.
- CH4 = configurable spare input for an additional local contact or test input.
- Bias/ground = E4 only if the selected analog front-end implementation supports it with an explicitly shown current-limiting network.

Do not label CH1 or CH2 as pure neural EEG. Temple signals can contain eye movement, facial muscle activity, motion artifact, and EEG. Make the electrode connector keyed, strain-relieved, finger-safe, and electrically isolated from charging contacts.

BIOPOTENTIAL SIGNAL CHAIN

Choose an available ADS1299-4/ADS1299 module or a technically equivalent EEG-oriented analog-front-end module with:

- At least 4 simultaneous differential channels.
- 24-bit conversion.
- Programmable gain.
- Suitable input-referred noise for microvolt biopotentials.
- 500 samples/s minimum per channel; 1,000 samples/s preferred.
- SPI or another deterministic digital interface.
- Lead-off/contact-check capability with bounded test current.
- Reference and bias support.

If using ADS1299, its analog supply must be approximately 5 V; do not power AVDD from 3.3 V. Show AVDD, DVDD, references, grounding, decoupling, startup sequencing, and the regulator/boost topology. Identify switching-converter frequencies and explain how switching noise is kept out of electrode inputs and the 0.5–100 Hz EEG band.

Show a preliminary, review-required electrode input-protection network for every body-connected lead. It must address current limiting, ESD, RF interference, AFE overvoltage, bias current, and lead-off current. Do not add a generic high-leakage or high-capacitance TVS directly to a microvolt input without analyzing its leakage, noise, and capacitance. Clearly mark every protection value that requires review by a qualified biopotential-instrumentation engineer.

CONTROLLER, BLE, TIMING, AND STORAGE

Use an nRF52840, nRF5340, or equivalent purchasable BLE 5 module with 2 Mbit/s PHY, hardware timers, SPI, watchdog, secure pairing, and firmware-update support.

Requirements:

- Acquire all AFE channels continuously.
- Preserve raw 24-bit sample words.
- Use one monotonic device timebase for AFE and IMU data.
- Timestamp resolution of 1 ms or better.
- Include an absolute sample counter that does not reset after BLE reconnect.
- Add a low-power 6-axis IMU sampled at 50–100 samples/s.
- Add a RAM or nonvolatile ring buffer for at least 60 seconds of full-rate data.
- Prefer local nonvolatile storage for a complete 60-minute session if a purchasable module fits the power and size constraints.
- Continue buffering during BLE interruption and support later recovery without duplicates.

At 4 channels × 1,000 samples/s × 24 bits, the raw AFE payload is 96 kbit/s before overhead. Verify the selected BLE module and phone-compatible settings can carry the batched stream. Use notifications, data-length extension, a large negotiated MTU, sequence numbers, timestamps, CRC/integrity checking, and packet-loss counters.

Define a versioned BLE data packet containing:

- Protocol version.
- Device ID and session ID.
- Packet type.
- Monotonic packet sequence number.
- First-sample device timestamp.
- First-sample absolute sample counter.
- Enabled-channel mask and sample-rate metadata.
- Batched interleaved signed 24-bit samples.
- Timestamped IMU samples, either batched or in a separate packet type.
- Battery, fault, contact/lead-off, buffer, and reset status.
- CRC or application-level integrity check.

Define control operations for identity/capabilities, safe predefined channel configuration, session start/stop, event marker insertion, status, storage query, buffered-data download, fault report, and reset-reason report.

Reserve device-ID and synchronization fields so a second pod can be added in a future phase, but do not include a second pod in this prototype.

POWER SYSTEM

Use a protected, certified single-cell Li-ion/LiPo battery. Design for at least 4 hours of continuous acquisition and BLE streaming, with a desired 6-hour runtime and at least 25% battery-capacity margin.

Provide a power budget with average and peak current for:

- Analog front end and every enabled channel.
- Analog boost/regulator losses.
- MCU and BLE radio at the proposed connection parameters.
- IMU.
- Local memory.
- Status indicators.
- Battery monitor and quiescent loads.

Include battery protection, state-of-charge reporting, controlled low-battery shutdown, rail sequencing, local decoupling, and an accessible hard power-off method.

CHARGING AND STORAGE CASE

Design a smart-ring-style storage case, but use recessed spring contacts or another simple docked-contact charger for the first prototype. Inductive charging may be shown only as an alternative with its heat, EMC, and efficiency tradeoffs.

Critical charging constraints:

- The pod operates from battery only while attached to electrodes.
- Charging is impossible while the pod is worn.
- Recording is disabled by a physical or hardware electrical interlock whenever charging, USB, or debugging is connected. Firmware alone is not sufficient.
- The electrode connector must be physically disconnected or electrically isolated in the charging orientation.
- No conductive path from mains-powered equipment, USB, charger, debugger, or oscilloscope may reach the electrodes.
- Include charger overvoltage, overcurrent, short-circuit, battery-temperature, and thermal protection.
- Show charge-state indication.

MECHANICAL DESIGN

Use a rounded reusable pod that sits primarily behind the ear, with a flexible adhesive tail extending toward the temple and jaw. The rigid pod must not press directly on the temple.

Module-based P1 targets:

- Preferred maximum pod envelope: approximately 60 × 35 × 18 mm.
- Preferred pod mass: below 30 g, excluding the case.
- No sharp edges.
- Battery mechanically retained and protected from puncture.
- Strain relief at the electrode-tail connector.
- Sweat- and incidental-splash-resistant construction for supervised tests, without claiming an IP rating.
- Replaceable electrode-tail alignment marks visible to the operator.

If the selected modules exceed these targets, show the actual dimensions, explain which modules set the size, and propose a later custom-PCB miniaturization path without pretending that path is already validated.

RECEIVER AND SESSION DATA

The receiver can initially be a simple phone or computer application concept. It must:

- Pair explicitly and use encrypted BLE.
- Show connection, battery, contact quality, buffer state, and packet-loss counters.
- Display raw traces plus optional non-destructive EEG and sEMG views.
- Insert timestamped experiment markers.
- Save raw packets and decoded samples.
- Detect duplicate, missing, reordered, malformed, and corrupted packets.
- Use pseudonymous study IDs and never broadcast a participant name or diagnosis.
- Store locally by default and provide export/delete controls.

Do not require cloud services.

SAFETY AND TESTING BOUNDARY

This design may not be attached to a person based solely on this generated plan.

Create a bench-first verification sequence:

1. Unpowered visual and continuity inspection.
2. Power-rail, sequencing, charging-interlock, current, and thermal tests.
3. Shorted-input noise and mains-interference measurement.
4. Biopotential-simulator tests for amplitude, frequency, gain, clipping, crosstalk, common-mode behavior, lead-off behavior, timing, and BLE integrity.
5. Forced BLE outage and local-buffer recovery.
6. Battery, charger, single-fault, and enclosure review by qualified engineers.
7. Human use only after qualified electrical/biomedical review and an appropriate consent/ethics process.

Never instruct the builder to connect electrodes while USB, a programmer, charger, oscilloscope, or other mains-referenced equipment is attached.

REQUIRED BLUEPRINT OUTPUT

Generate all of the following:

1. INFO: system purpose, non-goals, assumptions, limitations, and block diagram.
2. BOM: exact purchasable part/module numbers, quantities, dimensions, mass, voltage ranges, estimated cost, availability/source links, and clearly marked alternatives.
3. WIRING: pin-by-pin wiring and net names for electrodes, AFE, MCU, IMU, memory, power rails, charger, battery protection, interlock, status indicators, and connectors. Show all voltage levels and grounds.
4. POWER BUDGET: average/peak currents, conversion losses, estimated runtime, and thermal-risk notes.
5. DATA BUDGET: raw and packetized bit rates, BLE parameters, notification payload layout, buffering requirements, and worst-case outage behavior.
6. MECH: realistic module placement, enclosure dimensions, mass estimate, electrode-tail geometry, connector strain relief, case layout, and exploded assembly view.
7. INSTRUCTIONS: assembly and bring-up steps that keep body connection prohibited until all bench gates pass.
8. TEST PLAN: measurable tests and expected results for power, noise, simulator accuracy, timing, BLE loss, buffer recovery, contact detection, charging interlock, and temperature.
9. RISK/OPEN-ISSUE LIST: unsupported assumptions, parts that do not meet requirements, safety items requiring qualified review, and aspects Blueprint cannot validate.
10. MINIATURIZATION NOTES: only after the module design, identify which functions could move to a custom PCB and which measurements must be completed first.

Before finalizing, run electrical consistency checks for supply voltage, pin conflicts, unpowered ICs, overcurrent, battery/charger compatibility, regulator headroom, logic-level compatibility, SPI timing, and BLE throughput. Do not silently repair a requirement; report conflicts and propose options.
```

## Short iteration prompt

Use this after reviewing the first Blueprint result. Replace bracketed text with actual findings.

```text
Revise the NORT P1 design using the following engineering review findings:

[PASTE NUMBERED FINDINGS HERE]

Preserve these non-negotiable constraints:

- One module-based temple/behind-ear pod; no second pod yet.
- Six-contact replaceable Ag/AgCl hydrogel tail with dedicated bipolar sEMG witness channel.
- At least four simultaneous 24-bit AFE channels at 500 samples/s minimum, preferably 1,000.
- Correct ADS1299-class analog supply; never assume 3.3 V AVDD.
- Battery-only body-connected operation.
- Hardware/physical interlock preventing sensing while charging, USB, or debugging is connected.
- No stimulation and no medical, ALS, safety, or inner-speech-decoding claims.
- Local timestamps, sample counters, sequence numbers, integrity checking, BLE batching, and outage buffering.
- Realistic module dimensions, mass, current, runtime, and charging-case geometry.
- Bench simulator testing and qualified engineering review before any body attachment.

For every revision:

1. Show a change log mapping each finding to the exact design change.
2. Regenerate the affected BOM, wiring, power budget, data budget, mechanical layout, and instructions.
3. Re-run voltage, pin, current, power, SPI, and BLE consistency checks.
4. List unresolved conflicts explicitly.
5. Do not substitute a custom PCB unless the module-based option is proven impossible; if it is impossible, explain why and keep the custom PCB as a separate future design.
```

## Focused correction prompts

### Correct an unsafe charging path

```text
The current design may create a conductive path from the charger, USB, or debugger to body electrodes. Redesign the charging and debug architecture so body-connected acquisition is battery-only and recording is disabled by a hardware or physical interlock whenever charging or debugging is possible. Show the isolation/interlock circuit and mechanical connector states. Do not rely on firmware alone.
```

### Correct an invalid ADS1299 power rail

```text
The ADS1299 analog rail is invalid. Revise the power tree using the datasheet's valid AVDD/AVSS and DVDD operating ranges. Show regulator headroom, startup sequence, decoupling, ground strategy, switching frequency, ripple estimate, and the effect on the microvolt input signal. Recalculate battery runtime and thermal estimates.
```

### Correct unrealistic enclosure output

```text
The mechanical concept is smaller than the selected modules. Rebuild the enclosure from the actual module, battery, connector, wiring-bend, insulation, and clearance dimensions. Report the true bounding box and mass. Keep the rigid pod behind the ear and the temple/jaw portion flexible. Do not render a product-sized concept until the module assembly dimensions support it.
```

### Correct incomplete BLE integrity handling

```text
Revise the BLE protocol to make every missing, duplicate, reordered, malformed, or corrupted sample detectable. Include protocol version, device/session ID, packet sequence, absolute sample counter, device timestamp, enabled-channel mask, batched signed 24-bit samples, status, and integrity check. Add a 60-second local ring buffer and define reconnection recovery without resetting counters.
```
