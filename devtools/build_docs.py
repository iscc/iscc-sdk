"""Copy README.md to documentation site index.md."""
from os.path import abspath, dirname, join


HERE = dirname(abspath(__file__))
SRC = join(HERE, "../README.md")
DST = join(HERE, "../docs/index.md")
CHANGELOG_SRC = join(HERE, "../CHANGELOG.md")
CHANGELOG_DST = join(HERE, "../docs/changelog.md")


def main():
    """Copy README and CHANGELOG to do mkdocs documentation"""
    with open(SRC, "rt", encoding="utf-8") as infile:
        text = infile.read()
    with open(DST, "wt", encoding="utf-8", newline="\n") as outf:
        outf.write(text)

    with open(CHANGELOG_SRC, "rt", encoding="utf-8") as infile:
        text = infile.read()
    with open(CHANGELOG_DST, "wt", encoding="utf-8", newline="\n") as outf:
        outf.write(text)


if __name__ == "__main__":
    main()
