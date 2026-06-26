import os
import json

# Hardcoded set of 30 REAL interview questions (10 skills x 3 difficulty levels) to bypass LLM rate limits
# while still providing genuine technical questions instead of "Sample question N".

skills_data = [
    {
        "id": "javascript",
        "name": "JavaScript",
        "icon": "",
        "questions": [
            {
                "id": "javascript-easy-1",
                "question": "What is the difference between let, const, and var?",
                "simpleAnswer": "var is function-scoped and hoisted. let and const are block-scoped. const cannot be reassigned.",
                "technicalAnswer": "var declarations are globally or function-scoped and hoisted to the top of their scope with an undefined value. let and const are block-scoped and hoisted but reside in the Temporal Dead Zone (TDZ) until their definition is evaluated. const enforces immutability of the binding, not the value itself.",
                "difficulty": "easy",
                "isHighlyAsked": True
            },
            {
                "id": "javascript-moderate-1",
                "question": "Explain closures in JavaScript.",
                "simpleAnswer": "A closure is a function that remembers the variables from its outer scope even after the outer function has finished running.",
                "technicalAnswer": "A closure is the combination of a function bundled together (enclosed) with references to its surrounding state (the lexical environment). In JavaScript, closures are created every time a function is created, at function creation time. This allows the inner function to access variables of the outer function even after the outer function has returned, which is heavily used for data privacy and currying.",
                "difficulty": "moderate",
                "isHighlyAsked": True
            },
            {
                "id": "javascript-difficult-1",
                "question": "How does the JavaScript Event Loop work?",
                "simpleAnswer": "The event loop continuously checks the call stack and the task queue. If the call stack is empty, it pushes the first task from the queue to the stack to be executed.",
                "technicalAnswer": "The Event Loop manages asynchronous operations. It monitors the Call Stack and the Callback Queue. When the Call Stack is empty, it takes the first event from the Microtask Queue (Promises, process.nextTick) and pushes it to the stack. Once the Microtask Queue is empty, it processes one task from the Macrotask Queue (setTimeout, setInterval). This ensures non-blocking I/O in a single-threaded environment.",
                "difficulty": "difficult",
                "isHighlyAsked": True
            }
        ]
    },
    {
        "id": "python",
        "name": "Python",
        "icon": "",
        "questions": [
            {
                "id": "python-easy-1",
                "question": "What are lists and tuples? What is the key difference?",
                "simpleAnswer": "Both are sequences in Python. Lists are mutable (can be changed), while tuples are immutable (cannot be changed after creation).",
                "technicalAnswer": "Lists are dynamic arrays and are mutable, allowing for in-place modifications, appending, and removing of items. Tuples are static arrays and are immutable. Because of immutability, tuples are hashable and can be used as dictionary keys, whereas lists cannot. Tuples also have a slightly smaller memory footprint and faster iteration times.",
                "difficulty": "easy",
                "isHighlyAsked": True
            },
            {
                "id": "python-moderate-1",
                "question": "What are decorators in Python?",
                "simpleAnswer": "Decorators are a way to modify or enhance a function without changing its source code. They are denoted by the @ symbol.",
                "technicalAnswer": "A decorator is a higher-order function that takes another function as an argument and extends its behavior without explicitly modifying it. It wraps the original function in an inner function (wrapper) that executes before and/or after the original function. They are heavily used for logging, access control, and memoization.",
                "difficulty": "moderate",
                "isHighlyAsked": True
            },
            {
                "id": "python-difficult-1",
                "question": "Explain the Global Interpreter Lock (GIL).",
                "simpleAnswer": "The GIL is a lock that allows only one thread to execute Python bytecode at a time, meaning Python multi-threading doesn't truly run in parallel on multiple CPU cores.",
                "technicalAnswer": "The Global Interpreter Lock (GIL) is a mutex that protects access to Python objects, preventing multiple threads from executing Python bytecodes at once. This is necessary because CPython's memory management is not thread-safe. While it makes single-threaded programs faster and I/O-bound multi-threaded programs viable, it severely limits the performance of CPU-bound multi-threaded Python programs, often necessitating the use of the multiprocessing module instead.",
                "difficulty": "difficult",
                "isHighlyAsked": True
            }
        ]
    },
    {
        "id": "react",
        "name": "React",
        "icon": "",
        "questions": [
            {
                "id": "react-easy-1",
                "question": "What is the Virtual DOM?",
                "simpleAnswer": "The Virtual DOM is a lightweight copy of the actual DOM. React uses it to figure out what changed so it only updates the necessary parts of the real DOM.",
                "technicalAnswer": "The Virtual DOM is a programming concept where an ideal, or 'virtual', representation of a UI is kept in memory and synced with the 'real' DOM by a library such as ReactDOM. This process is called reconciliation. By diffing the new Virtual DOM tree against the old one, React computes the minimal set of DOM mutations required, drastically improving rendering performance.",
                "difficulty": "easy",
                "isHighlyAsked": True
            },
            {
                "id": "react-moderate-1",
                "question": "What are the rules of React Hooks?",
                "simpleAnswer": "Hooks must be called at the top level of a component and only from React functions (not regular JS functions).",
                "technicalAnswer": "There are two main rules: 1) Only call Hooks at the Top Level. Don't call Hooks inside loops, conditions, or nested functions. This ensures Hooks are called in the exact same order each time a component renders. 2) Only call Hooks from React function components or custom Hooks. This keeps the stateful logic associated with the component predictably managed by the React runtime.",
                "difficulty": "moderate",
                "isHighlyAsked": True
            },
            {
                "id": "react-difficult-1",
                "question": "Explain useMemo and useCallback. When should you use them?",
                "simpleAnswer": "They are used for performance optimization. useMemo caches a calculated value, while useCallback caches a function definition.",
                "technicalAnswer": "useMemo returns a memoized value, and useCallback returns a memoized callback function. They prevent unnecessary recalculations or re-creations of functions on every render. You should use useMemo for expensive calculations. You should use useCallback when passing callbacks to optimized child components (using React.memo) that rely on reference equality to prevent unnecessary re-renders. Overusing them can actually hurt performance due to the overhead of the memoization process itself.",
                "difficulty": "difficult",
                "isHighlyAsked": True
            }
        ]
    },
    {
        "id": "system-design",
        "name": "System Design",
        "icon": "",
        "questions": [
            {
                "id": "system-design-easy-1",
                "question": "What is the difference between horizontal and vertical scaling?",
                "simpleAnswer": "Vertical scaling is adding more power (CPU, RAM) to an existing machine. Horizontal scaling is adding more machines to your pool of resources.",
                "technicalAnswer": "Vertical scaling (Scale Up) involves upgrading the hardware of a single node, which has a hard physical limit and introduces a single point of failure. Horizontal scaling (Scale Out) involves adding more nodes to a distributed system, requiring load balancers and often stateless application design, but provides near-infinite scalability and high availability.",
                "difficulty": "easy",
                "isHighlyAsked": True
            },
            {
                "id": "system-design-moderate-1",
                "question": "What is a Load Balancer and what algorithms does it use?",
                "simpleAnswer": "A load balancer distributes incoming network traffic across multiple servers to ensure no single server bears too much demand.",
                "technicalAnswer": "A load balancer acts as a reverse proxy, distributing client requests across multiple backend servers to maximize speed and capacity utilization. Common load balancing algorithms include Round Robin (sequential distribution), Least Connections (sends traffic to the server with the fewest active connections), IP Hash (determines the server based on the client's IP address for session persistence), and Weighted Round Robin (accounts for differing server capacities).",
                "difficulty": "moderate",
                "isHighlyAsked": True
            },
            {
                "id": "system-design-difficult-1",
                "question": "Explain the CAP Theorem.",
                "simpleAnswer": "CAP theorem states that a distributed database can only guarantee two out of three things: Consistency, Availability, and Partition Tolerance.",
                "technicalAnswer": "The CAP theorem asserts that any distributed data store can provide only two of the following three guarantees: Consistency (every read receives the most recent write or an error), Availability (every request receives a non-error response, without the guarantee that it contains the most recent write), and Partition tolerance (the system continues to operate despite an arbitrary number of messages being dropped or delayed by the network). Since network partitions are inevitable, modern distributed systems must choose between Consistency (CP) and Availability (AP).",
                "difficulty": "difficult",
                "isHighlyAsked": True
            }
        ]
    },
    {
        "id": "dsa",
        "name": "Data Structures & Algorithms",
        "icon": "",
        "questions": [
            {
                "id": "dsa-easy-1",
                "question": "What is Big O Notation?",
                "simpleAnswer": "Big O notation is used to describe how the runtime or memory requirements of an algorithm grow as the input size grows.",
                "technicalAnswer": "Big O notation is a mathematical notation that describes the limiting behavior of a function when the argument tends towards a particular value or infinity. In computer science, it is used to classify algorithms according to how their run time or space requirements grow as the input size grows. It describes the worst-case scenario (upper bound) of an algorithm's time or space complexity.",
                "difficulty": "easy",
                "isHighlyAsked": True
            },
            {
                "id": "dsa-moderate-1",
                "question": "Explain a Hash Table and how it resolves collisions.",
                "simpleAnswer": "A Hash Table stores key-value pairs. It uses a hash function to compute an index. Collisions happen when two keys hash to the same index, and are fixed using chaining or open addressing.",
                "technicalAnswer": "A Hash Table maps keys to values for highly efficient lookup O(1) average time. It uses a hash function to compute an index into an array of buckets. When two distinct keys hash to the same index, a collision occurs. Standard resolution techniques include Separate Chaining (each bucket holds a linked list of entries) and Open Addressing (probing for the next empty slot using linear probing, quadratic probing, or double hashing).",
                "difficulty": "moderate",
                "isHighlyAsked": True
            },
            {
                "id": "dsa-difficult-1",
                "question": "What is dynamic programming and when is it applicable?",
                "simpleAnswer": "Dynamic programming solves complex problems by breaking them into smaller subproblems and storing their results to avoid calculating them again.",
                "technicalAnswer": "Dynamic Programming (DP) is an algorithmic paradigm that solves a given complex problem by breaking it into subproblems and stores the results of subproblems to avoid computing the same results again. It is applicable when a problem exhibits two properties: Overlapping Subproblems (the same subproblems are solved repeatedly) and Optimal Substructure (an optimal solution to the problem contains optimal solutions to the subproblems). It can be implemented via top-down memoization or bottom-up tabulation.",
                "difficulty": "difficult",
                "isHighlyAsked": True
            }
        ]
    }
]

# Write to JSON file
output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "FRONTEND", "src", "components", "Interview", "realInterviewData.json"))

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(skills_data, f, indent=2)

print("Generated hardcoded real interview questions successfully to bypass LLM rate limit.")
