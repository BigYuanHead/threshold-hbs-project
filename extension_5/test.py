from benchmark.src.bench_ots_compare import benchmark_winternitz_by_w

def main():
    for w in [4, 8, 16]:
        print(f"\nTesting w={w}")
        try:
            rows = benchmark_winternitz_by_w(
                total_keys=4,
                n_parties=3,
                w_values=[w],
                repeats=1,
            )
            print("passed")
            print(rows[0])
        except Exception as e:
            print("failed")
            print(type(e).__name__, e)

if __name__ == "__main__":
    main()