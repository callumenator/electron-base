import React, { useState } from 'react';

export default function Heading() {
    const [counter, setCounter] = useState(0);
    return (
        <>
            <h1>Hello</h1>
            <div>{counter}</div>
            <button onClick={() => setCounter(v => v + 1)}>Click</button>
        </>
    );
}
