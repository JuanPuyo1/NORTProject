# NORT Phase 1 Prototype Requirements

## 1. Product definition

### 1.1 Working name

NORT P1 — Single-Pod Signal-Quality Wearable.

### 1.2 Intended use

NORT P1 is a battery-operated research data recorder worn at one temple and behind the ear. It records local biopotentials, a dedicated facial-muscle channel, and motion data, then streams timestamped samples to a nearby phone or computer over Bluetooth Low Energy.

It is intended to validate:

- Electrode placement and attachment.
- Signal stability on hairless temple/behind-ear skin.
- Separation and labeling of local EEG, eye, muscle, and motion signatures.
- BLE throughput, packet integrity, and reconnection behavior.
- Pod comfort, temperature, battery life, and charging workflow.

### 1.3 Explicit non-goals

P1 will not:

- Decode words, thoughts, or continuous inner speech.
- Generate synthesized speech from neural signals.
- Diagnose, monitor, prevent, or treat any condition.
- Be tested on patients or people with ALS.
- Apply electrical stimulation.
- Operate while charging, connected to USB, or connected to mains-powered test equipment.
- Be described as medical-grade, clinically validated, or compliant with medical-device standards.

## 2. System concept

The system consists of four replaceable or reusable assemblies:

1. **Reusable electronics pod** — analog front end, MCU/BLE radio, IMU, local memory, battery, protection, and status indication.
2. **Disposable electrode tail** — flexible adhesive carrier with pre-gelled Ag/AgCl contacts and a keyed connector to the pod.
3. **Charging/storage case** — mechanically locates the pod, charges through recessed contacts, and prevents simultaneous recording.
4. **Receiver** — a phone or computer application that records packets, displays channel quality, and inserts experiment markers.

The first build should use purchasable modules and evaluation boards. The enclosure may be larger than the long-term product. Custom miniaturized PCBs are deferred until acquisition quality is measured.

## 3. Electrode montage

### 3.1 Baseline six-contact layout

- **E1 — anterior temple:** local biopotential sensing.
- **E2 — posterior temple/upper preauricular area:** local biopotential sensing.
- **E3 — mastoid or hairless area behind the ear:** shared reference.
- **E4 — lower behind-ear area:** bias/ground return, subject to qualified review.
- **E5 and E6 — lower temporalis or upper jaw:** bipolar sEMG witness pair.

The exact geometry must be adjustable during fit testing. The design must not assume that every local biopotential channel is neural EEG.

### 3.2 Initial channel map

- **CH1:** E1 relative to E3, EEG/EOG mixture.
- **CH2:** E2 relative to E3, EEG/EOG mixture.
- **CH3:** E5 relative to E6, dedicated bipolar temporalis/jaw sEMG.
- **CH4:** configurable spare channel for an additional local electrode, electrode experiment, or diagnostic input.
- **BIAS:** E4 only after the bias network and patient-current limits have been reviewed.

If a selected module cannot implement this mapping safely, Blueprint must flag the incompatibility rather than silently changing the montage.

### 3.3 Electrode-tail requirements

- Single-user, replaceable adhesive tail.
- Pre-gelled Ag/AgCl contacts preferred for P1.
- Supplier documentation for skin-contact materials must be retained.
- Adhesive must tolerate at least 60 minutes of normal head movement without requiring excessive skin pressure.
- Tail must mechanically strain-relieve every electrode trace.
- Connector must be keyed and finger-safe, with no battery or charging voltage exposed.
- Electrode labels must be visible during application.
- No conductive adhesive or electrode area may bridge adjacent contacts.

## 4. Electrical architecture

### 4.1 Analog front end

Target an ADS1299-4, ADS1299, or equivalent EEG-oriented module with:

- At least four simultaneous differential channels.
- 24-bit conversion.
- Programmable channel gain.
- Input-referred noise appropriate for microvolt biopotentials.
- 500 samples/s minimum per enabled channel; 1,000 samples/s preferred to retain useful facial sEMG bandwidth.
- Lead-off/contact-check capability with bounded current.
- Configurable reference and bias support.
- SPI or another deterministic digital interface.

ADS1299 designs require an approximately 5 V analog supply and a valid digital supply. Blueprint must show the complete analog and digital power rails and must not power the ADS1299 analog rail from 3.3 V.

### 4.2 Controller and BLE

Use an nRF52840, nRF5340, or equivalent BLE 5 module with:

- 2 Mbit/s PHY support.
- SPI bandwidth adequate for continuous AFE acquisition.
- Hardware timers for sample timestamps.
- A watchdog.
- Secure device identity and encrypted BLE pairing/bonding capability.
- Firmware-update support that cannot run while electrodes are attached.

The first build may use a certified radio module to reduce RF-layout risk.

### 4.3 Motion sensing

Provide a low-power 6-axis accelerometer/gyroscope module:

- At least 50 samples/s.
- Timestamped in the same device timebase as biopotential data.
- Configurable range suitable for normal head motion.
- Used for artifact labeling, not medical motion assessment.

### 4.4 Local storage

Provide a ring buffer sufficient for at least 60 seconds of full-rate data during BLE interruption. Prefer nonvolatile flash sufficient for one complete 60-minute session if module size and power permit.

Local data must be recoverable after a BLE disconnect. The receiver must not be the sole lossless copy unless testing proves zero-loss behavior.

### 4.5 Input protection

Every electrode-connected path must include a reviewed protection network that addresses:

- Current limiting under single faults.
- ESD at the connector and electrode tail.
- RF rectification and out-of-band interference.
- AFE input range and recovery after saturation.
- Bias and lead-off current limits.
- No low-impedance path to battery, charging contacts, USB, or debugger.

Generic high-capacitance TVS parts must not be added directly to low-noise inputs without checking leakage and noise. Component values require review by a qualified biopotential-instrumentation engineer.

## 5. Power and charging

### 5.1 Worn operation

- Protected, certified single-cell Li-ion/LiPo battery.
- Minimum target runtime: 4 hours of continuous recording and BLE streaming.
- Desired runtime: 6 hours.
- Battery state reported to the receiver.
- Measured enclosure surface temperature rise must remain within the review checklist limit.
- Low-battery shutdown must preserve stored data and avoid uncontrolled AFE states.

### 5.2 Power tree

Blueprint must provide:

- Battery protection and fuel/state monitoring.
- Low-noise digital rail.
- Correct AFE analog rail.
- Sequencing and decoupling requirements.
- Estimated average and peak currents for AFE, MCU/radio, IMU, memory, and conversion losses.
- Battery capacity calculation with at least 25% engineering margin.

Switching converters must be physically and electrically separated from electrode inputs. Their switching frequency, harmonics, layout, and filtering must be reviewed against the intended 0.5–100 Hz EEG band and broader sEMG band.

### 5.3 Charging case

The P1 case should use recessed spring contacts or another simple docked-contact method. Inductive charging may be proposed only as an alternative because it adds heat, EMC, and efficiency risks.

Required charging behavior:

- Charging is possible only when the pod is removed from the body and seated in the case.
- A physical or hardware-enforced interlock disables all electrode sensing during charging.
- Firmware alone is not the only interlock.
- The electrode connector cannot be attached in the charging orientation, or recording inputs are physically isolated.
- Charge status is visible without exposing live conductors.
- Case and pod include appropriate overcurrent, overvoltage, short-circuit, and thermal protection.
- No “charge while wearing” mode exists.

## 6. Mechanical and usability requirements

### 6.1 Module-based P1 targets

- Pod target envelope: no larger than approximately 60 × 35 × 18 mm unless selected modules make this impossible.
- Pod target mass: below 30 g, excluding the charging case.
- Rounded enclosure with no sharp edges.
- No rigid part should press directly on the temple.
- Electronics should sit primarily behind the ear, with the flexible tail extending to the temple and jaw.
- Enclosure must resist sweat and incidental splashes during supervised experiments; no ingress-protection rating is claimed.
- Battery must be retained so that a drop cannot pull or puncture it.

Blueprint must report the actual estimated dimensions and mass. It must not show a ring-sized or invisible concept if the selected modules cannot fit.

### 6.2 Application workflow

1. Inspect skin and electrode tail.
2. Clean and dry the application area using the approved electrode-supplier procedure.
3. Attach the disposable tail using labeled placement landmarks.
4. Connect and seat the reusable pod.
5. Confirm contact quality before recording.
6. Start a session from the receiver.
7. Stop the session and confirm data finalization.
8. Remove the pod and tail without pulling electrode traces.
9. Dispose of or store the tail according to its validated reuse policy.
10. Charge only after the pod is disconnected from the electrode tail.

## 7. Sampling and signal handling

### 7.1 Acquisition settings

Initial settings:

- Biopotentials: 1,000 samples/s per enabled channel preferred; 500 samples/s permitted for early integration.
- IMU: 50–100 samples/s.
- Raw resolution: preserve the AFE's 24-bit sample words.
- No irreversible onboard high-pass filtering unless raw DC-capable data are also retained.
- Receiver may display a 0.5–40 Hz EEG view and a wider sEMG view, but stored source data remain raw.
- Mains notch filtering is optional in visualization and must be recorded in metadata.

### 7.2 Clock and event requirements

- Every sample block carries a monotonic device timestamp.
- Timestamp resolution: 1 ms or better.
- Desired clock drift: below 100 ppm; actual drift must be measured.
- Receiver event markers include device timestamp, receiver timestamp, event code, and optional text.
- Reconnection must not reset the session sample counter.
- Architecture reserves fields for future multi-pod identity and synchronization.

## 8. BLE data contract

Each notification should contain:

- Protocol version.
- Device ID and session ID.
- Packet type.
- Monotonic packet sequence number.
- First-sample device timestamp.
- First-sample absolute sample counter.
- Sample rate and enabled-channel mask when configuration changes.
- Batched interleaved 24-bit channel samples.
- Optional batched IMU samples or a separate timestamped IMU packet.
- Battery and status flags.
- Contact/lead-off flags.
- CRC or application-level integrity check.

Control messages must support:

- Read device and firmware identity.
- Read capabilities.
- Configure channels, gains, and sample rate within safe predefined limits.
- Start and stop a session.
- Insert an event marker.
- Query storage and packet-loss counters.
- Download buffered data.
- Report faults and reset reasons.

The receiver must record raw packets and a decoded session file. It must detect duplicate, missing, reordered, and malformed packets.

## 9. Privacy and security

- Use random per-device identifiers; do not broadcast a participant name or diagnosis.
- Require an explicit pairing action.
- Encrypt BLE links using platform-supported secure pairing.
- Store recordings locally by default.
- Associate participant information through a separate pseudonymous study ID.
- Provide a documented delete/export workflow.
- Never upload recordings to a cloud service without separate informed consent and a defined retention policy.

## 10. Phase 1 verification states

Human attachment is not the first test state.

1. **Unpowered inspection:** assembly, connector isolation, battery retention, and polarity.
2. **Power-only bench test:** rails, sequence, current, charging interlock, thermal behavior, and faults.
3. **Shorted-input test:** AFE noise and interference.
4. **Biopotential-simulator test:** amplitude, frequency response, gain, clipping, channel crosstalk, timestamps, and BLE integrity.
5. **Artifact fixture test:** cable/tail motion and ESD robustness within approved bench procedures.
6. **Qualified design review:** electrical, battery, skin-contact, mechanical, and study-protocol review.
7. **Limited healthy-adult feasibility:** only under the approved consent/ethics process.

## 11. Acceptance criteria

P1 passes only when all mandatory criteria are met:

- Streams continuously for at least 60 minutes at the selected channel count and sample rate.
- Receiver-observed missing samples are below 0.1% and every loss is explicitly detectable.
- Local buffering recovers a forced BLE outage of at least 30 seconds without duplicate or missing samples.
- Sample-counter discontinuities, packet corruption, and device resets are zero during the acceptance session.
- Device/receiver clock mapping remains within 10 ms over 60 minutes after correction; raw measured drift is documented.
- Contact status identifies an intentionally disconnected electrode.
- A simulator signal is recovered within ±5% amplitude and ±1% frequency over the tested range.
- Shorted-input noise and mains interference are measured and accepted by the qualified reviewer against the selected AFE/module specification.
- Rest, blink/eye movement, jaw contraction, overt speech, and normal head-motion segments are visibly and statistically distinguishable in the expected witness channels.
- No classification of imagined words is required.
- Worn enclosure temperature and skin response remain within the pre-approved test limits.
- Device cannot acquire electrode data while charging or physically connected to USB/debug equipment.
- Session metadata records hardware, firmware, electrode-tail lot, montage, gains, sample rates, filters, battery state, and test operator.

## 12. Phase exit decision

After acceptance testing, choose exactly one next path:

- **Single-pod continuation:** local EEG remains stable and carries useful information beyond sEMG/EOG witnesses.
- **Bilateral comparison:** add a second synchronized pod only if wider spatial coverage has a defined experimental benefit.
- **Broader scalp benchmark:** use a 12–32 channel research montage if local signals are too weak or confounded.
- **sEMG-first assistive path:** pursue residual-muscle communication separately and label it accurately.
- **Stop/revise:** redesign electrodes, mechanics, or analog acquisition if signal stability or safety criteria fail.

Any later inner-speech study must use held-out recording days and compare EEG-only, sEMG-only, and combined performance before making a neural-decoding claim.
