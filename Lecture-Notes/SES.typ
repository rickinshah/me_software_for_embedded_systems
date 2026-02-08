#set page(
  paper: "a4"
)
#set par(justify: true)
#set heading(numbering: "1.")
#show title: set align(center)

#let note(body) = block(
  inset: 12pt,
  fill: luma(240),
  radius: 6pt,
  stroke: gray,
)[
  #strong[Note:] #body
]

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
  #linebreak()
  Jitter - uncertain
  #linebreak()
  Delay - certain
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

#strong[Persistence:] Duration between when task enters to termination.

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


= Bounded Buffer Problem
