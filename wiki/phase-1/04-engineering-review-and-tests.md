# NORT Phase 1 Engineering Review and Test Gate

## Purpose

Use this document to evaluate Blueprint's generated design and every subsequent hardware revision. A checked box means the item was verified against a schematic, datasheet, measurement, or qualified review—not merely mentioned by an AI-generated document.

Record for every review:

- Design revision:
- Blueprint project/export:
- Hardware revision:
- Firmware revision:
- Electrode-tail revision and lot:
- Reviewer names and qualifications:
- Review date:
- Open issues:
- Final decision: `REJECT`, `REVISE`, `BENCH TEST`, or `APPROVE FOR SPECIFIED NEXT GATE`.

No single reviewer should approve work outside their competence. Human attachment requires separate electrical/biomedical, battery/mechanical, skin-contact, and study-protocol approval.

## Gate 0 — Blueprint output completeness

Reject the generated design before engineering review if any mandatory output is missing.

- [ ] System block diagram identifies all body-connected and non-body-connected subsystems.
- [ ] BOM contains exact orderable modules/parts, quantities, voltage ranges, dimensions, mass, cost, and source links.
- [ ] Alternatives are clearly separated from selected parts.
- [ ] Wiring is pin-by-pin and labels every rail, signal, connector, and ground.
- [ ] Electrode mapping identifies E1–E6, CH1–CH4, reference, and bias.
- [ ] Power budget includes average and peak currents plus converter losses.
- [ ] Battery runtime includes at least 25% engineering margin.
- [ ] BLE data budget includes payload and protocol overhead.
- [ ] Mechanical output uses actual selected-module dimensions.
- [ ] Charging case and pod are both represented.
- [ ] Assembly instructions preserve the no-body-contact bench gates.
- [ ] Test plan contains numeric measurements and pass criteria.
- [ ] Open assumptions and unresolved conflicts are listed.
- [ ] No inner-speech, medical-grade, clinical, safety, or ALS-readiness claim appears.

## Gate 1 — Architecture review

### 1.1 Scope and signal integrity

- [ ] The device is a recorder only; there is no stimulation output.
- [ ] CH1 and CH2 are described as mixed local biopotentials, not pure EEG.
- [ ] CH3 is a physically separate bipolar sEMG witness channel.
- [ ] The spare channel does not share an unsafe or undocumented return.
- [ ] Reference and bias functions are not confused.
- [ ] Eye, muscle, motion, cable, and mains artifacts are included in the experiment plan.
- [ ] Raw samples are retained before optional display filters.
- [ ] AFE gain and input range accommodate both microvolt EEG and larger sEMG/artifacts without persistent saturation.
- [ ] Sample rate is at least 500 samples/s per enabled channel.
- [ ] AFE channels are sampled simultaneously or inter-channel timing is documented.

### 1.2 Parts and availability

- [ ] Every selected module has a manufacturer datasheet or schematic.
- [ ] Module pinout matches Blueprint's wiring.
- [ ] Modules are currently purchasable from a traceable supplier.
- [ ] No obsolete, counterfeit-prone, or unspecified battery part is selected.
- [ ] Radio module has the required BLE features and accessible firmware toolchain.
- [ ] AFE module exposes the necessary differential inputs, reference, bias, data-ready, SPI, and power pins.
- [ ] Selected memory supports the required write bandwidth and endurance.
- [ ] IMU supports timestamp-compatible sampling at 50–100 samples/s.

## Gate 2 — Electrical and body-connected safety review

This gate requires a qualified electrical or biomedical instrumentation reviewer.

### 2.1 Power rails

- [ ] ADS1299-class AVDD/AVSS is within the datasheet's recommended range.
- [ ] DVDD and every logic interface are within valid ranges.
- [ ] No 5 V signal reaches a 3.3 V-only input.
- [ ] Regulator dropout/headroom is valid across battery voltage and peak load.
- [ ] Startup and shutdown cannot leave electrode inputs in an uncontrolled powered state.
- [ ] Analog and digital decoupling follows the selected AFE/module requirements.
- [ ] Ground strategy avoids routing charging or radio current through the analog return.
- [ ] Switching regulator frequency and harmonics are evaluated against acquisition bands.
- [ ] Ripple/noise measurements are planned at every rail and at the AFE output.

### 2.2 Electrode paths

- [ ] Every electrode lead has a documented maximum possible current under normal operation.
- [ ] Every electrode lead has a documented maximum possible current under relevant single faults.
- [ ] Series current limiting is placed so one component failure does not defeat all protection where required by the reviewer.
- [ ] Bias-drive amplitude, bandwidth, stability, and output current are analyzed.
- [ ] Lead-off test frequency and current are documented and bounded.
- [ ] ESD protection leakage, capacitance, and noise are compatible with microvolt acquisition.
- [ ] RF filtering does not destabilize or materially degrade the AFE.
- [ ] Connector pins cannot expose battery, charger, or digital-rail power to skin contacts.
- [ ] A wrong or partially inserted connector does not create an unsafe state.
- [ ] Unused AFE inputs are terminated according to the datasheet.
- [ ] AFE input common-mode and differential range are valid for the montage.
- [ ] Electrode disconnection and AFE saturation recover predictably.

### 2.3 Charging and debug isolation

- [ ] Acquisition is powered only by the internal battery while electrodes are connected.
- [ ] A hardware or mechanical interlock disables acquisition during charging.
- [ ] Firmware is not the sole charging interlock.
- [ ] Electrode tail cannot remain electrically body-connected in the charging configuration.
- [ ] USB, SWD/JTAG, UART, oscilloscope, bench supply, or other wired debug cannot be connected during body attachment.
- [ ] Debug connectors are inaccessible in the worn configuration or controlled by an equivalent reviewed mechanism.
- [ ] Charger fault conditions cannot energize electrode contacts.
- [ ] Charging contacts are recessed and protected from accidental shorting.
- [ ] Charging stops or remains safe for battery overtemperature, undertemperature, overvoltage, and timeout faults.

### 2.4 Battery and thermal

- [ ] Cell has traceable manufacturer data and appropriate transport/safety documentation.
- [ ] Cell includes suitable protection or is paired with a reviewed protection circuit.
- [ ] Charge voltage and current match the exact cell.
- [ ] Battery is protected from puncture, crushing, bending, and cable pull.
- [ ] No rigid sharp feature can contact the pouch cell.
- [ ] Worst-case component dissipation is estimated.
- [ ] Temperature sensors are placed where they detect relevant battery/charger heating.
- [ ] Thermal shutdown behavior is hardware-supported where practical.
- [ ] Enclosure materials and venting do not create an unreviewed battery hazard.

## Gate 3 — RF, firmware, and data review

### 3.1 BLE capacity

- [ ] Raw payload is recalculated from actual channels, sample rate, and bits/sample.
- [ ] Packet headers, integrity fields, and IMU traffic are included.
- [ ] Selected connection interval, MTU, data length, PHY, and notifications support the required sustained rate.
- [ ] The design does not depend on a phone-specific maximum without testing target phones.
- [ ] Radio peak current is included in rail and battery calculations.
- [ ] Antenna keep-out and enclosure effects follow module guidance.
- [ ] AFE and electrode traces are separated from antenna and RF-current loops.

### 3.2 Packet integrity

- [ ] Protocol has an explicit version.
- [ ] Device ID and session ID are present.
- [ ] Every stream packet has a monotonic sequence number.
- [ ] Every sample has an unambiguous absolute sample-counter position.
- [ ] Device timestamps use a monotonic hardware-backed timebase.
- [ ] Channel order, sign extension, byte order, and 24-bit encoding are specified.
- [ ] Configuration changes are represented in the data stream.
- [ ] Integrity check detects malformed/corrupted application payloads.
- [ ] Receiver reports missing, duplicate, reordered, and corrupted packets.
- [ ] Device reset reason and counter reset are unmistakable.
- [ ] Session finalization records total generated, transmitted, buffered, recovered, and lost samples.

### 3.3 Buffering and recovery

- [ ] Ring-buffer capacity is calculated for at least 60 seconds.
- [ ] Buffer wrap behavior is deterministic and reported.
- [ ] BLE transmission cannot block AFE acquisition.
- [ ] Storage writes cannot cause missed samples.
- [ ] Reconnect does not reset session or sample counters.
- [ ] Recovery protocol prevents duplicate samples.
- [ ] Power loss produces a detectable incomplete session.
- [ ] Nonvolatile data have a documented export and delete path.

### 3.4 Security and privacy

- [ ] Pairing requires physical user action or equivalent explicit authorization.
- [ ] BLE uses authenticated encryption supported by the platform.
- [ ] Advertising data contain no participant name, diagnosis, or recording content.
- [ ] Study IDs are pseudonymous.
- [ ] Stored files have access controls appropriate to the receiver platform.
- [ ] No cloud upload occurs by default.
- [ ] Data retention, export, deletion, and consent boundaries are documented.
- [ ] Firmware update is authenticated and unavailable during body connection.

## Gate 4 — Mechanical, electrode, and usability review

### 4.1 Mechanical truthfulness

- [ ] CAD/enclosure dimensions come from actual module and battery models.
- [ ] Clearance exists for connectors, insulation, wiring bend radius, antenna keep-out, and assembly.
- [ ] Actual estimated pod dimensions and mass are reported.
- [ ] Rigid electronics sit primarily behind the ear.
- [ ] No rigid edge or concentrated battery load presses on the temple.
- [ ] Enclosure edges are rounded.
- [ ] Pod cannot detach and hang from electrode traces.
- [ ] Battery remains retained after the defined drop test.
- [ ] Charging case cannot close on a misaligned cell/pod in a hazardous way.
- [ ] Sweat paths cannot bridge charging contacts to electrode contacts.
- [ ] No ingress-protection claim is made without testing.

### 4.2 Electrode tail and skin contact

- [ ] Electrode material and gel are identified as Ag/AgCl and compatible electrolyte.
- [ ] Adhesive and all skin-contact materials have supplier documentation.
- [ ] Intended contact duration is defined.
- [ ] Tail geometry accommodates left/right head use or identifies a side-specific version.
- [ ] E1–E6 placement labels are visible.
- [ ] Electrodes cannot overlap or electrically bridge in normal placement.
- [ ] Flex traces tolerate the planned bend and removal cycles.
- [ ] Connector and tail have strain relief.
- [ ] Removal method limits skin injury.
- [ ] Reuse/disposal policy is explicit.
- [ ] Skin inspection and stop criteria are included in the human protocol.

## Gate 5 — Bench test plan

For every test, record setup photographs, equipment model/serial number, calibration status, ambient conditions, hardware/firmware revision, raw files, calculated result, operator, and reviewer.

### 5.1 Unpowered inspection

- [ ] Verify BOM and assembly against schematic.
- [ ] Verify polarity and component orientation.
- [ ] Verify no shorts between battery, charging, digital, analog, and electrode nets.
- [ ] Measure resistance from every electrode pin to all power/charging/debug pins.
- [ ] Exercise connector keying and partial insertion.
- [ ] Inspect battery retention, insulation, and enclosure.
- [ ] Confirm the charging orientation disconnects or isolates electrode inputs.

Pass condition: no undocumented connection, polarity error, exposed conductor, mechanical battery risk, or body-to-charger path.

### 5.2 Power-rail bring-up

- [ ] Power initially from an appropriately current-limited isolated bench setup with no electrode/body connection.
- [ ] Measure inrush, idle, acquisition, BLE, storage-write, and peak radio current.
- [ ] Measure every rail at minimum, nominal, and maximum expected battery voltage.
- [ ] Capture rail ripple and transients with acquisition and radio active.
- [ ] Verify power sequencing and controlled shutdown.
- [ ] Trigger low-battery handling.
- [ ] Verify watchdog and reset-reason reporting.

Pass condition: all rails remain in datasheet ranges, current matches the reviewed budget within agreed tolerance, and no unsafe or unexplained transient occurs.

### 5.3 Charging and interlock

- [ ] Confirm charge voltage/current against cell specification.
- [ ] Test normal completion, recharge threshold, and charge-state reporting.
- [ ] Attempt to start acquisition while docked.
- [ ] Attempt to attach the electrode connector in charging orientation.
- [ ] Remove/reinsert pod during charging.
- [ ] Test approved charger fault simulations.
- [ ] Measure pod, battery, charger, and case temperatures.

Pass condition: acquisition and electrode connection are physically/electrically prevented during charging, charging remains within reviewed electrical/thermal limits, and firmware cannot override the interlock.

### 5.4 Shorted-input noise

- [ ] Configure AFE at each intended gain and sample rate.
- [ ] Short inputs using the AFE manufacturer's recommended test arrangement.
- [ ] Record at least 10 minutes on battery with enclosure closed.
- [ ] Repeat with BLE idle and continuously transmitting.
- [ ] Compute input-referred RMS and peak-to-peak noise.
- [ ] Plot power spectral density and identify mains, converter, clock, and radio spurs.
- [ ] Compare channels and check crosstalk.

Pass condition: numeric limit must be set by the qualified reviewer from the selected module specification and intended signal bandwidth. Any unexplained periodic spur is a failure pending investigation.

### 5.5 Biopotential-simulator accuracy

Inject only through an approved isolated biopotential/EEG simulator.

- [ ] Test zero input and known sine amplitudes across the intended microvolt range.
- [ ] Test frequencies spanning at least 0.5–100 Hz.
- [ ] Test a larger sEMG-like signal on CH3.
- [ ] Test common-mode input within the reviewed range.
- [ ] Test near-clipping and recovery.
- [ ] Test electrode disconnect/lead-off detection.
- [ ] Test channel-to-channel crosstalk.
- [ ] Compare streamed and locally recovered samples.

Pass conditions:

- Recovered amplitude within ±5% over the approved test range.
- Recovered frequency within ±1%.
- No undocumented inversion, byte-order error, clipping, or sample reordering.
- Contact flag identifies an intentionally disconnected electrode.
- Crosstalk and common-mode rejection meet reviewer-set limits.

### 5.6 Timing and BLE integrity

- [ ] Run four AFE channels at the selected production sample rate.
- [ ] Run IMU, status, and event-marker traffic simultaneously.
- [ ] Test every target phone/computer receiver.
- [ ] Record continuously for at least 60 minutes.
- [ ] Count generated, received, duplicated, reordered, malformed, CRC-failed, and missing packets/samples.
- [ ] Measure device clock drift against a calibrated reference.
- [ ] Insert known periodic hardware or simulator events and measure timestamp error.
- [ ] Force 5-, 15-, and 30-second BLE outages.
- [ ] Reconnect and recover buffered data.
- [ ] Test receiver restart and out-of-range recovery.

Pass conditions:

- Missing receiver samples below 0.1%, with every loss detected.
- Zero unexplained sample-counter discontinuities.
- Zero duplicate samples after recovery.
- Forced 30-second outage fully recovered from local buffering.
- Device/receiver clock mapping within 10 ms over 60 minutes after documented correction.
- No device reset or AFE acquisition interruption.

### 5.7 Runtime and thermal

- [ ] Start from a normally charged battery.
- [ ] Run full-rate acquisition, IMU, BLE, and storage continuously.
- [ ] Log battery voltage/state and temperatures.
- [ ] Repeat in charging case for a normal full charge.
- [ ] Inspect enclosure and battery after testing.

Pass conditions:

- At least 4 hours continuous runtime.
- Controlled shutdown preserves and finalizes recoverable data.
- Temperature remains within limits defined before testing by the qualified reviewer.
- No swelling, odor, deformation, discoloration, or unstable charge behavior.

### 5.8 Mechanical and attachment fixture

- [ ] Perform connector insertion/removal cycles.
- [ ] Flex the disposable-tail fixture through intended motion.
- [ ] Apply defined cable/pod pull loads using a fixture, not a person.
- [ ] Perform the reviewed drop test with battery installed.
- [ ] Check enclosure closure, charging alignment, and strain relief afterward.
- [ ] Repeat shorted-input and simulator tests after mechanical stress.

Pass condition: no exposed conductor, battery movement, cracked enclosure, connector damage, loss of isolation, or material signal degradation.

## Gate 6 — Pre-human review

Completing bench tests does not automatically authorize human use.

- [ ] All Gates 0–5 passed with signed evidence.
- [ ] Every safety-critical open issue is closed.
- [ ] Qualified electrical/biomedical reviewer approves the exact body-connected configuration.
- [ ] Battery/mechanical reviewer approves the enclosed worn assembly.
- [ ] Skin-contact materials and contact duration are reviewed.
- [ ] Study protocol has appropriate ethics/IRB determination, consent, privacy, and adverse-event procedures.
- [ ] Inclusion/exclusion and stop criteria are written.
- [ ] Operator is trained in application, monitoring, removal, and emergency response.
- [ ] No wired charging, debug, or mains-referenced instrument is present during attachment.
- [ ] A fresh visual inspection and self-test are required before every session.

Initial human feasibility, if separately approved, should be limited to healthy adults and acquisition tasks:

- Rest.
- Eyes open/closed.
- Blink and horizontal eye movement.
- Jaw contraction.
- Overt speech.
- Quiet head movement.

It should not involve ALS participants or claim inner-speech decoding.

## Gate 7 — Phase 1 acceptance and go/no-go

### Mandatory acceptance

- [ ] 60-minute complete acquisition session passes timing and integrity limits.
- [ ] 30-second BLE interruption is recovered without duplicate or missing samples.
- [ ] Simulator amplitude and frequency accuracy pass.
- [ ] Shorted-input noise and interference are accepted by the reviewer.
- [ ] Contact detection works for deliberate disconnection.
- [ ] Charging/body-connection interlock cannot be bypassed by normal use or firmware.
- [ ] Four-hour runtime passes.
- [ ] Thermal and mechanical tests pass.
- [ ] Session metadata are complete.
- [ ] Approved feasibility data show expected witness-channel responses for eye, jaw, overt speech, and motion tasks.
- [ ] No safety-critical issue remains open.

### Decision rules

Choose **GO — retain one pod** only if local channels remain stable and provide useful information after obvious sEMG, EOG, and motion segments are identified.

Choose **GO — compare a second pod** only if a written hypothesis requires bilateral coverage and synchronization can be tested independently.

Choose **GO — broader scalp benchmark** if local signals are too small, spatially ambiguous, or dominated by artifacts.

Choose **GO — sEMG-first research** if the muscle channel is useful but EEG does not add measurable information. This path must be described as residual-muscle sensing, not neural reading.

Choose **NO-GO / REDESIGN** for any unresolved body-current, charging, battery, thermal, signal-integrity, data-loss, or skin-contact problem.

## Later decoding gate

Word or command decoding is outside Phase 1. Before any later neural-decoding claim:

- Use multiple recording days.
- Split evaluation by held-out session/day, not random neighboring trials.
- Compare EEG-only, sEMG-only, EOG/motion-only, and combined models.
- Use permutation-derived chance levels and confidence intervals.
- Report balanced accuracy, false activations per minute, calibration time, and information-transfer rate.
- Demonstrate that EEG adds predictive information beyond muscle, eye, cue timing, and motion.
- Replicate before considering an ALS observational study.
