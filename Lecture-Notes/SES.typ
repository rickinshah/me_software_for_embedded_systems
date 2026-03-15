#set page(
  paper: "a4",
  margin: (x: 2.2cm, y: 2cm),
)

#set par(
  justify: true,
  leading: 0.6em,   // improves readability
)

#set text(
  font: "Libertinus Serif", // fantastic academic font
  size: 11pt,
)

#set heading(
  numbering: "1.",
)

#show heading.where(level: 1): set text(15pt, weight: "bold")
#show heading.where(level: 2): set text(13pt, weight: "semibold")

#show raw: set text(
// font: "JetBrainsMono Nerd Font",
size: 9pt,
)

#show title: set align(center)

#let callout(title, color, body) = block(
  inset: 12pt,
  radius: 6pt,
  stroke: color,
  fill: color.lighten(88%),
)[
  #strong[#title:] #linebreak() #body
]

#let note(body) = callout("Note", gray, body)

#let homework(body) = callout(
  "Homework",
  rgb(220, 80, 70),
  body
)

#let important(body) = callout(
  "Important",
  rgb(200, 140, 20),
  body
)

#let example(body) = callout(
  "Example",
  rgb(60, 120, 200),
  body
)

#let defn(body) = callout(
  "Definition",
  blue,
  body
)

#title[Software for Embedded Systems]
#outline()

#pagebreak()

= Linux for Embedded Systems

- A kernel for RTES - `Prempt RT`.
- Linux has 4 components:
  - Kernel
  - Shared Libraries -- can be called by any program
  - System command & Utilities 
  - User apps

- *Kernel* and *Shared Libraries* are in *Kernel Space*.
- *System Command* and *User apps* are in *User Space*.

== Linux Kernel

- Includes *Daemon* proceses.
- *Init* is a process that initiates Daemon processes. It always has *PID 1*.
- `systemctl list-units --tyye =service`.

= Tasks & Task Management

#strong[Embedded Systems] - reactive in nature.

#note[
  - Jitter - uncertain
  - Delay - certain
]

== Tasks

- Embedded program - collection of firmware modules.
- Firmware modules executes - Process/Task.
- Control ensures that tasks execution satisfies set of timing constraints - *Real Time*

*Process is allocated following resources:*
- *CPU*
  - PC
  - SP
  - General Purpose Registers
  - Status/Flag Registers
- *Stack/Heap*
- *TCB creation*

#defn[
  *Persistence:* Duration between when task enters to termination.
]

=== Thread
- Lightweight process
- can share resources
- doesn't require separate address space

#strong[Thread Types]

- Interleaved - 3th
- Blocked
- Simultaneous - 4th

#figure(
  image("assets/2026-02-05-10-42-24.png", width: 80%),
  caption: [Thread Types],
) <fig-2026-02-05-10-42-24>

#note[
  *Hyperthreading*(Intel) and *Simultaneous*(ARM) are the same thing.
]

= Shared Variables

#figure(
  image("assets/2026-02-05-09-40-02.png", width: 80%),
  caption: [Shared Variables],
) <fig-2026-02-05-09-40-02>

- Producer - checks for not full - `Bool Full()`;
- Consumer - checks for not empty - `Bool Empty()`;

*Atomicity* - Either the task will complete or won't start.

== Ping Pong Buffer

#figure(
  image("assets/2026-02-05-09-42-42.png", width: 50%),
  caption: [Ping Pong Buffer],
) <fig-2026-02-05-09-42-42>

- When producer is writing into `B0`, consumer is reading from `B1` or vice versa.
- So one buffer at a given time will be used by either producer or consumer.

== Ring Buffer

#figure(
  image("assets/2026-02-05-09-46-49.png", width: 40%),
  caption: [Ring Buffer],
) <fig-2026-02-05-09-46-49>

- `T0` and `T1` will start from the same buffer.
- `T0` is producer and `T1` is consumer.

== MailBox

#figure(
  image("assets/2026-02-05-09-51-05.png", width: 40%),
  caption: [MailBox],
) <fig-2026-02-05-09-51-05>

- `Producer` or `post` will send message.
- `Consumer` or `pend` will recieve message.

#note[
- For *streaming*, Direct Communication is used.
- For *controlling*, Indirect communication is used.
]

= Task Synchronization

#figure(
  image("assets/2026-02-04-11-09-32.png", width: 60%),
  caption: [Co-operating Tasks],
) <fig-2026-02-04-11-09-32>

- `count` is shared variable. We need to use mutex.

== Active Resource
Active resource ends up being consumed.
- Examples:
  - CPU
  - Memory (depending on how it is accessed)

== Passive Resource

- Memory
- Bus

== Requirements

- Mutial exlusion
- Deadlock
- Bounded Waiting - n tasks can run before the waiting of the current task stops.

== Solution

=== Flags
- Each Task has a flag
- Atomic procedure await

#figure(
  image("assets/2026-02-04-11-27-47.png", width: 60%),
  caption: [],
) <fig-2026-02-04-11-27-47>

*Cons*
- Doesn't work with multiple tasks.

=== Token Passing

#figure(
  image("assets/2026-02-04-11-31-38.png", width: 60%),
  caption: [],
) <fig-2026-02-04-11-31-38>

*Cons*
  - Starvation of lower proiority task.

=== Manage using interrupts

- Disallow interrupts in the critical section.

= Semaphores

- Two purposes:
  - Threads are going to execute in particular order.
  - Mutual Exclusion

- wait - `p(s)` -> set flag
- signal - `v(s)` -> reset flag

#figure(
  image("assets/2026-02-04-13-34-23.png", width: 60%),
  caption: [Semaphores - Critical Resources],
) <fig-2026-02-04-13-34-23>

#figure(
  image("assets/2026-02-04-13-36-05.png", width: 60%),
  caption: [Semaphores],
) <fig-2026-02-04-13-36-05>

== Spin Locking and Busy Waiting

#figure(
  image("assets/2026-02-04-13-47-10.png", width: 60%),
  caption: [Spin Locking and Busy Waiting],
) <fig-2026-02-04-13-47-10>

- *It is given in Textbook that `Binary Semaphores` are `Mutex`. But that is wrong.*
  - Mutex has ownership.
  - Linux uses *futexes*.

== Semaphores - Counting

#figure(
  image("assets/2026-02-04-13-49-53.png", width: 60%),
  caption: [Counting Semaphores],
) <fig-2026-02-04-13-49-53>

== Implementation
```
typedef struct {
    int value;
    queue tlist;
} semaphore;
```

= Example - Mars Rover

#figure(
  image("assets/2026-02-04-13-56-52.png", width: 60%),
  caption: [Requirements],
) <fig-2026-02-04-13-56-52>

== Semphores:
- `mutex(1)`
- `empty(n-1)`
- `full(0)`

#figure(
  image("assets/2026-02-04-13-54-57.png", width: 50%),
caption: [Consumer & Producer],
) <fig-2026-02-04-13-54-57>

#figure(
  image("assets/2026-02-04-13-55-48.png", width: 50%),
  caption: [Semaphores],
) <fig-2026-02-04-13-55-48>

#defn[
  *Uncontended* descibes cases where a thread doesn't have any competition to acquire a lock.
  *Contended* describes a or lock that different threads are trying to acquire at the same time.
]

#homework[
- What is `futexes`?
  - `Fast User Space Mutex`
  - Uncontended -> User space - manages lock.
  - Contended -> Kernel space - manages sleeping and waking threads.
  - 0 - uncontended, 1 - available, -1(or any negative) - contended
  - `FUTEX_WAIT` & `FUTEX_WAKE`
  - #link("https://linux.die.net/man/7/futex")[Man Page]
]

= Bounded Buffer Problem

- Multiple Readers can read simultaneously.
- Only one Writer can write.


#figure(
  image("assets/2026-02-09-11-45-43.png", width: 80%),
caption: [Reader Writer Problem],
) <fig-2026-02-09-11-45-43>

- Cannot use `mutex` cause the reader which locks `wrtSem` may not be the same reader which unlocks `wrtSem` so we have to use `BinarySemaphore`.

= Monitors

- Encapsulating the critical resource.
- Provides control by allowing only one process to access a critical resource at a time.
- Built-in mutual exclusion, no manual `wait()` and `signal()` required.
- `put()` and `get()` are the two procedures available.

= Operating System

== Boot Loader

- UEFI can have 128+ partition and BIOS can have max 4 partition.
- Reset address for x86 - 0xFFFF followed by 0s.
- First part of BootLoader is immutable. So when BIOS update is there, it doesn't update the first part.
- Second stage - GPIO and Pin MUX and maybe peripherals
- Initramfs [Init Ram File System] - Temp(Dummy) file system before the actual file system is mounted.
- Third Stage - vmlinux, initramfs.img

- MBR(master boot record) - Sector 0
- VBR(variable boot record)

BIOS
- Sector 0 (512 Bytes)
  - 0 - 455 -> Boot Loader Program
  - 446 - 509 -> Partition allowed (4 paritions)
  - 510 - 512 -> 0x55AA
- no Secure Boot and security mechanisms
- Slower
- cant exceed 2Tb - Logical Block Address that was allowed that is 32 bits. so 2^32 allowed. Block size was limited 512 bytes.
- Text-based Interface

UEFI
- upto 64 bits. block size upto 4kb. -> 2^64 x 4kb.
- GPT (Graphic Partition Table)
- supports Secure Boot and sinature verification
- Faster
- Graphical Interface


== Secure Boot
- Every part of boot image is going to be having a digital signature.
- Binary image -> Hash -> Sign with Private Key.
  - Platform Key (pk)
  - Key exchange Key (kek)
  - Signature DB (db)
- db-x is a set of invalid signature.
- db is set of valid signature.
- UEFI(inside NVRAM - non-corruptable)
  - Will have crypto engine to verify.
  - Enables CPU, RAM and interconnect buses(PCIe).
  - Checks if Secure Boot or not.
  - UEFI loads EFI(Extended Firmware Interface) System Partition -> EFI/ubuntu/shimx64.efi
  - Checks the digital signature then loads the .efi.
  - shim verifies grub.
- UEFI
  - SHIM
    - GRUB
      - vmlinux and initramfs
        - Each stage checks verifies digital singature.
- When kernel loads modules it will check the digital sinature against Signature DB (db).
- Boot ROM in SoC(Embedded Systems) instead of UEFI.

- Boot ROM
  - RoT
    - SPL
      - UBoot
        - Kernel loaded


Only UEFI and Boot ROM is executed and everything else is loaded then checked against digital sinatures and then allowed to executed.

- First user space program that is loaded is *Init()* i.e., *PID 1*.

- Public Key is derived from the private key.

message -> hash -> signed with private key -> verify with public key

== Init
- Generally runs at level 3 - without graphics, with network, multi user
- Newer Systemd, earlier System V Init
- Single user is used for recovery.

- 0 -halt
- 1 - single user
- 2 - multi user
- 3 - network, multi user
- Level 5 - Graphical
- Level 6 - Reboot

- SysV sequential
- systemd parallely starts services.

== Inodes

- ext4 as example - Linux
- Inodes - Data structure used by linux file system to store the metadata of the file.
- File type, file size, owner, group id, user id, permissions, timestamp
- Timestamps - A time - creation, m time -modified, c time - change in metadata
- Link Count
- file < 4096 kb ? or kB? it will be in 1 block.
- ext -> extent data -> logical block address to upto where file is oing to be stored.
- can have multiple extent entry
- Entry
  - Length
  - Start
  - How many block?
- Extent tree

- MBR - 512 x 8

- rm -> mark inode as empty, data is already there in data blocks. physical blocks don't get lost.
- access data - `testdisk`
- in windows, it doesnt even delete, it just changes the first name to `$`. we can get back the file.
- Smallest file still takes 4kB in linux.

#homework[
  use `testdisk` and recover a file
]

== Linux File System

- `initfs` make use of `/bin`

= Data - Features

- Data -> Information -> Knowledge

== Big Data
- High frequency
- large amount of data
- format the data comes in

== Data Engineering

- Get data and format into particular format
- *Kalman Filtering*

- The baker's 

== Deciles vs Quartiles
- Mean and Median is not helpful for outliers
- So we find the quartiles or deciles

= AI vs ML vs DL vs GenAI

- When we provide Set of rules then it is called AI
- When the system is going to learn the rules by itself then it is ML. We don't define rules.
- ML with neural networks is DL
- DL - CNN, RNN, Transformation
- Transformation -> GenAI
- Generate complete schedule/a series of values like timestamp + lux instead of single value
- GenAI with human understandable language -> LLM


== On the fly vs Batch
- On the fly -> Reinforcement Learning

== Type of Learning
- Instance - only consider current instance/ lazy learning. e.g. KNN


== Standard Scalar

- (x - mean) / std

- Mostly used Target encoding - average price for a item (may overfit your data)

- Label Encoding should mostly used when data is randomized
