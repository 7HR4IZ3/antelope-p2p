export function nanoseconds() {
    const loadNs = process.hrtime();
    const loadMs = new Date().getTime();
    const diffNs = process.hrtime(loadNs);
    return BigInt(loadMs) * BigInt(1e6) + (BigInt(diffNs[0]) * BigInt(1e9) + BigInt(diffNs[1]));
}
