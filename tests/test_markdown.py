from axon.markdown import preprocess_logseq


def test_preprocess_logseq(contents):
    assert (
        preprocess_logseq(contents("md/logseq.md"))
        == """\
- # title
  |||
  |-:|-|
  |key|value|
\t- content
\t  |||
\t  |-:|-|
\t  |key1|value1|
\t  |key2|value2|
\t- ignored"""
    )
