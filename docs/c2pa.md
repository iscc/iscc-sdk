# **ISCC** - C2PA Soft Bindings

A [C2PA](https://c2pa.org) manifest is attached to an asset by a hard binding (a cryptographic
hash). When the manifest gets stripped, for example by a platform that re-encodes uploads, a **soft
binding** lets you find the manifest again from the content alone.

`iscc-sdk` creates ISCC soft bindings with the algorithm `io.iscc.v0`, as specified by
[IEP-0020](https://ieps.iscc.codes/iep-0020/). It does the media extraction, the ISCC generation and
the byte encoding for you, and gives you the finished `c2pa.soft-binding` assertion. You only add it
to your manifest and sign as usual.

## Quick start

Run the command on the file you are about to sign:

```shell
uvx "iscc-sdk[c2pa]" soft-binding photo.jpg
```

It prints the assertion for a C2PA manifest definition as JSON on stdout:

```json
{
  "label": "c2pa.soft-binding",
  "created": true,
  "data": {
    "alg": "io.iscc.v0",
    "blocks": [
      {
        "scope": {},
        "value": [0, 7, 104, 227, 117, 199, 163, 217, 54, 188, 109, 0, 98, 225, 117, 146, ...]
      }
    ],
    "bindingMetadata": {
      "informationalUrl": "https://ieps.iscc.codes/iep-0020/",
      "io.iscc.generator": {
        "name": "iscc-sdk",
        "version": "0.9.7"
      }
    }
  }
}
```

The `value` (shortened above) is the ISCC-SEQ: the ISCC-UNITs of the asset as bytes. The units
themselves go to stderr, one per line, so stdout stays clean for piping:

```text
ISCC:AADWRY3VY6R5SNV4NUAGFYLVSJ3I7KX37VO6PYLC22DFONVH2GVZIPY
ISCC:CEDQYWTPK2Q7ZTK47HPOYUUTO3TCAZ6KNVUZODFMMY42S6O7RDCWFEA
ISCC:EED4GQZQTY6J5DTHNDQ7S7EGNENJNRTEGLGHFWXFGNDZHSMO4HEZGZI
ISCC:GAD6Z2VJLX46FD6QVSSCW3BOUAIV5GRINTAHISA6UQIHPLWH3YBGAHQ
ISCC:IADVKUU37LS33M6VGDCS6RGRHTGWU7DRB5RWEDOC3MOEHRKZFLRNZFY
```

Add `--no-semantic` to leave out the Semantic-Codes. This needs no `c2pa` extra:

```shell
uvx iscc-sdk soft-binding --no-semantic photo.jpg
```

The command exits with a non-zero code and a message on stderr if anything goes wrong.

## Python API

```python
import iscc_sdk as idk

sb = idk.soft_binding("photo.jpg")  # semantic=True by default
sb.units  # ["ISCC:AAD...", "ISCC:CED...", "ISCC:EED...", "ISCC:GAD...", "ISCC:IAD..."]
sb.value  # bytes, the ISCC-SEQ (content of blocks[].value)

assertion = idk.soft_binding_definition(sb)  # dict, the JSON shown above
```

Install the extra for Semantic-Codes with `pip install "iscc-sdk[c2pa]"`, or pass `semantic=False`.

## Signing with a C2PA SDK

Put the assertion into the `assertions` of your manifest definition and sign the **same file** you
created the soft binding from:

```python
import json
import iscc_sdk as idk

manifest = {
    "claim_generator_info": [{"name": "my-app", "version": "1.0"}],
    "assertions": [idk.soft_binding_definition(idk.soft_binding("photo.jpg"))],
}
with open("manifest.json", "w") as f:
    json.dump(manifest, f)
```

```shell
c2patool photo.jpg -m manifest.json -o signed.jpg
```

The same manifest definition works with the c2pa-rs `Builder` and its bindings, such as
`c2pa-python`. `"created": true` lists the assertion in `created_assertions`, so it is attributed to
the signer, as IEP-0020 requires.

!!! note "Value encoding"

    C2PA SDKs before c2pa-rs PR 2757 store the `value` integer array as a CBOR array of integers, later
    versions as a CBOR byte string. IEP-0020 requires readers to accept both, so the same JSON works
    with old and new SDKs.

## What goes into the soft binding

Every ISCC-UNIT is Version 0 with a 256-bit body, always in this order:

| Order | ISCC-UNIT     | Included                                                   |
| ----- | ------------- | ---------------------------------------------------------- |
| 1     | Meta-Code     | only if the embedded metadata has a title                  |
| 2     | Semantic-Code | image and text, unless `--no-semantic` / `semantic=False`  |
| 3     | Content-Code  | image, audio, video and text (see the exceptions below)    |
| 4     | Data-Code     | always                                                     |
| 5     | Instance-Code | always                                                     |

- **Whole file, as signed.** The file is processed as it is, nothing is removed or normalized first.
    Create the soft binding from the final rendition you sign, not from the original you edited.
- **No file name fallback.** Without an embedded title there is no Meta-Code, so renaming a file
    does not change its soft binding.
- **Featureless images.** Uniform colors, plain gradients and similar images get an Image-Code that
    matches unrelated images. It is left out with a warning (see `is_featureless_image_code`).
- **Unsupported file types** get a Data-Code and an Instance-Code only, with a warning. They can be
    matched at byte level only.
- **Documents without text.** If no text can be extracted (a scanned or blank PDF), the Semantic-
    and Content-Code are left out with a warning, because an empty text would match every other
    empty document.
- **Semantic-Codes are never dropped silently.** If they are on and `iscc-sci` (images) or
    `iscc-sct` (text) is missing, the command fails with an install hint, so the same file always
    gives the same soft binding.
- **Binding metadata.** `bindingMetadata` links to IEP-0020 (`informationalUrl`), so viewers can
    explain the value, and names `iscc-sdk` and its version. Each iscc-sdk version
    pins the minor version of the semantic models, so the version also tells which models created
    the Semantic-Codes.

## Test vectors

Test vectors for implementers ship with the package as
[`iscc_sdk/c2pa_vectors.json`](https://github.com/iscc/iscc-sdk/blob/main/iscc_sdk/c2pa_vectors.json).
Each vector names an input file from [iscc-samples](https://github.com/iscc/iscc-samples) (or embeds
the input bytes) with its SHA-256, and gives the expected ISCC-UNITs, the value as hex, and the
value as base64 (the form used by the Soft Binding Resolution API). They are created without
Semantic-Codes, because neural network models can differ in single bits across platforms.

## API Reference

::: iscc_sdk.c2pa
    options:
        members: ["SoftBinding", "soft_binding", "soft_binding_definition"]
