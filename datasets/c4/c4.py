# coding=utf-8
# Copyright 2020 The TensorFlow Datasets Authors and the HuggingFace Datasets Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Lint as: python3
"""C4 dataset based on Common Crawl."""


import gzip
import json

import datasets


logger = datasets.logging.get_logger(__name__)


_DESCRIPTION = """\
A colossal, cleaned version of Common Crawl's web crawl corpus.

Based on Common Crawl dataset: "https://commoncrawl.org".

This is the processed version of Google's C4 dataset by AllenAI.

"""
_CITATION = """
@article{2019t5,
    author = {Colin Raffel and Noam Shazeer and Adam Roberts and Katherine Lee and Sharan Narang and Michael Matena and Yanqi Zhou and Wei Li and Peter J. Liu},
    title = {Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer},
    journal = {arXiv e-prints},
    year = {2019},
    archivePrefix = {arXiv},
    eprint = {1910.10683},
}
"""
_URL = "https://github.com/allenai/allennlp/discussions/5056"

_VARIANTS = ["en", "realnewslike", "en.noblocklist", "en.noclean"]

_N_SHARDS_PER_SPLIT = {
    "en": {"train": 1024, "validation": 8},
    "realnewslike": {"train": 512, "validation": 1},
    "en.noblocklist": {"train": 1024, "validation": 8},
    "en.noclean": {"train": 7168, "validation": 64},
}

_DATA_URL = (
    "https://huggingface.co/datasets/allenai/c4/resolve/main/{name}/c4-{split}.{index:05d}-of-{n_shards:05d}.json.gz"
)


class C4(datasets.GeneratorBasedBuilder):
    """C4, a colossal, cleaned version of Common Crawl's web crawl corpus."""

    BUILDER_CONFIGS = [datasets.BuilderConfig(name) for name in _VARIANTS]

    def _info(self):
        return datasets.DatasetInfo(
            description=_DESCRIPTION,
            features=datasets.Features(
                {
                    "text": datasets.Value("string"),
                    "timestamp": datasets.Value("string"),
                    "url": datasets.Value("string"),
                }
            ),
            supervised_keys=None,
            homepage=_URL,
            citation=_CITATION,
        )

    def _split_generators(self, dl_manager):
        data_urls = {}
        for split in ["train", "validation"]:
            n_shards = _N_SHARDS_PER_SPLIT[self.config.name][split]
            data_urls[split] = [
                _DATA_URL.format(name=self.config.name, split=split, index=index, n_shards=n_shards)
                for index in range(n_shards)
            ]
        downloaded_files = dl_manager.download(data_urls)
        return [
            datasets.SplitGenerator(name=datasets.Split.TRAIN, gen_kwargs={"filepaths": downloaded_files["train"]}),
            datasets.SplitGenerator(
                name=datasets.Split.VALIDATION, gen_kwargs={"filepaths": downloaded_files["validation"]}
            ),
        ]

    def _generate_examples(self, filepaths):
        """This function returns the examples in the raw (text) form by iterating on all the files."""
        id_ = 0
        for filepath in filepaths:
            logger.info("generating examples from = %s", filepath)
            with gzip.open(open(filepath, "rb"), "rt", encoding="utf-8") as f:
                for line in f:
                    if line:
                        example = json.loads(line)
                        yield id_, example
                        id_ += 1
