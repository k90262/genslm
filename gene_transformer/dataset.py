import torch
from torch.utils.data import Dataset
from Bio import SeqIO  # type: ignore[import]
from transformers import PreTrainedTokenizerFast
import numpy as np

class GenomeDataset(Dataset):
    def __init__(
            self, fasta_file: str, block_size: int, tokenizer: PreTrainedTokenizerFast
    ) -> None:
        """PyTorch Dataset that tokenizes sequences by codon.

        Parameters
        ----------
        fasta_file : str
            Path to fasta file to read sequence from.
        block_size : int
            max_length of :obj:`tokenizer` encoder.
        tokenizer : PreTrainedTokenizerFast
            Converts raw strings to tokenized tensors.
        """

        seq_records = list(SeqIO.parse(fasta_file, "fasta"))
        self.tokenized_sequences = []
        for s in seq_records:
            self.tokenized_sequences.extend(self.create_token_set_from_record(s, tokenizer=tokenizer,
                                                                              block_size=block_size))

    def create_token_set_from_record(self, s, tokenizer, block_size=512):
        sequence = str(s.seq.upper())
        sequence = " ".join(sequence[i: i + 3] for i in range(0, len(sequence), 3))
        sequence = "[START] " + sequence + " [END]"
        out = tokenizer.encode(sequence, max_length=block_size, return_overflowing_tokens=True)
        if len(out[-1]) != block_size:
            padded_last_chunk = list(np.pad(out[-1], (0, block_size - len(out[-1])), mode="constant",
                                            constant_values=fast_tokenizer.vocab["[PAD]"]))
            out = out[:-1]
            out.append(padded_last_chunk)
        return out

    def __len__(self) -> int:
        return len(self.tokenized_sequences)

    def __getitem__(self, idx: int) -> torch.Tensor:
        return torch.tensor(self.sequences[idx])  # type:ignore[no-any-return]


class FASTADataset(Dataset):  # type: ignore[type-arg]
    def __init__(
            self, fasta_file: str, block_size: int, tokenizer: PreTrainedTokenizerFast, alphabet: str = "codon"
    ) -> None:
        """PyTorch Dataset that tokenizes sequences by codon.

        Parameters
        ----------
        fasta_file : str
            Path to fasta file to read sequence from.
        block_size : int
            max_length of :obj:`tokenizer` encoder.
        tokenizer : PreTrainedTokenizerFast
            Converts raw strings to tokenized tensors.
        """

        self.alphabet = alphabet

        if self.alphabet == "codon":
            grouping = self.group_by_codon
        else:
            grouping = self.group_by_aa

        # Read in the sequences from the fasta file, convert to
        # codon string, tokenize, and collect in tensor
        self.sequences = torch.cat(  # type: ignore[attr-defined]
            [
                tokenizer.encode(
                    grouping(seq),
                    return_tensors="pt",
                    max_length=block_size,
                    padding="max_length",
                )
                for seq in SeqIO.parse(fasta_file, "fasta")
            ]
        )

    def group_by_codon(self, s: SeqIO.SeqRecord) -> str:
        """Split SeqRecord by codons, return as a string with whitespace.
        eg. 'AAACCC' -> 'AAA CCC'"""
        seq = str(s.seq)
        return " ".join(seq[i: i + 3] for i in range(0, len(seq), 3))

    def group_by_aa(self, s: SeqIO.SeqRecord) -> str:
        seq = str(s.seq).upper()
        return " ".join(i for i in seq)

    def __len__(self) -> int:
        return len(self.sequences)

    def __getitem__(self, idx: int) -> torch.Tensor:
        return self.sequences[idx]  # type:ignore[no-any-return]
