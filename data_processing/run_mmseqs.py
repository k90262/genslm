import subprocess
from pathlib import Path
from argparse import ArgumentParser


def parse_tsv(tsv_path: Path) -> int:

    raw_data = tsv_path.read_text()
    cluster_centers = []
    cluster_members = []
    for line in raw_data.strip().split("\n"):
        cluster_center, cluster_member = line.split()
        cluster_centers.append(cluster_center)
        cluster_members.append(cluster_member)

    cluster_centers = set(cluster_centers)
    cluster_members = set(cluster_members)

    return len(cluster_centers)


def mmseqs2_easy_cluster(fasta: Path, output_dir: Path, similarity: float, mmseqs_exe: str = "mmseqs") -> int:
    """Run easy-cluster mmseqs2 executable and return the number of non redundant sequences.

    Parameters
    ----------
    fasta : Path
        Path to fasta file.
    output_dir : Path
        Output directory for mmseqs2 executable.
    similarity : float
        min-seq-id similarity for mmseqs2.
    mmseqs_exe : str
        mmseqs executable path.
    """

    # Setup up and run mmseqs2 executable
    output_dir.mkdir(exist_ok=True)
    out_dir_and_files = output_dir / f"sim{similarity}"
    temp_dir = output_dir / "temp"
    command = f"{mmseqs_exe} easy-cluster {fasta} {out_dir_and_files} {temp_dir} --min-seq-id {similarity}"
    proc = subprocess.run(command.split())

    if proc.returncode == 0:
        print(f"\n\nSuccesfully clustered input fasta file to: {output_dir}")
    else:
        print(proc.stderr)
        print(f"Command: {command}")
        raise RuntimeError("MMSEQS did not sucessfully complete")

    # Determine number of clusters in data

    tsv_file = list(output_dir.glob("*.tsv"))[0]
    return parse_tsv(tsv_file)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--fasta", type=Path, required=True, help="Path to the fasta file input")
    parser.add_argument(
        "--output_dir",
        type=Path,
        required=True,
        help="Path to the output directory, will be made if it does not exist",
    )
    parser.add_argument(
        "--out_ext",
        type=str,
        help="Extension to give the output files names, defaults to 'res'",
        default="res",
    )
    parser.add_argument(
        "--mmseqs",
        type=str,
        help="Path to MMSEQS program",
        default="mmseqs",
    )
    parser.add_argument(
        "--similarity",
        type=float,
        default=0.5,
        help="Similarity threshold to run mmseqs with",
    )

    args = parser.parse_args()
    mmseqs2_easy_cluster(args.fasta, args.output_dir, args.similarity, args.mmseqs)
