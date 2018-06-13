# Paradrop Voice

This is an add-on module for Paradrop that provides text-to-speech and
speech recognition capabilities.

## Building paradrop-voice

The project is designed to be built as a snap. This requires snapcraft
to be installed on the development machine. It is recommended to use an
Ubuntu machine since that is the target environment for the snapcraft
developers. If you are using Ubuntu, run `sudo apt-get install snapcraft`.

Then run `snapcraft build` to build the paradrop-voice snap. If successful,
it should produce a file named paradrop-voice\_$version\_$architecture.snap.
The resulting snap file can be installed on a paradrop node.

## Voice API

The paradrop-voice module exposes its functions through an HTTP API. It
listens on port 8278 so as not to compete with the other services running
on a Paradrop node.

### Check the Service Status

Get status information from the paradrop-voice service including whether
it is currently decoding speech and what keyword, if any, it is expecting.

GET /status

```json
{
    "in_speech": false,
    "search": "paradrop"
}
```

### List Recognized Phrases

The paradrop-voice maintains a small history of recognized speech, which
can be retrieved with this endpoint.

GET /phrases

```json
[
    {
        "search": "enable",
        "text": "enable",
        "time": 1528925671.293648
    }
]
```

### Create a New Prompt

A prompt is the basic unit of interaction with the paradrop-voice service.
When the service handles a prompt, it plays the provided message using
text-to-speech, then waits for the search text to be spoken or for the
timeout to expire.

Creating a prompt through this endpoint returns immediately with an
object containing the prompt id. The caller can use this prompt id to
check the status of the prompt.

POST /prompts

```json
{
    "message": "If you would like to turn on this feature, say enable.",
    "search": "enable",
    "timeout": 20
}
```

Response

```
{
    "created_time": 1528926166.0225773,
    "detected": false,
    "detected_time": null,
    "id": 2,
    "message": "If you would like to turn on this feature, say enable.",
    "played": false,
    "played_time": 1528926166.0246336,
    "search": "enable",
    "search_started": false,
    "search_started_time": null,
    "timed_out": false,
    "timeout": 20
}
```

### Check the Status of a Prompt

GET /prompts/:id

```json
{
    "created_time": 1528926166.0225773,
    "detected": false,
    "detected_time": null,
    "id": 2,
    "message": "If you would like to turn on this feature, say enable.",
    "played": true,
    "played_time": 1528926166.0246336,
    "search": "enable",
    "search_started": true,
    "search_started_time": 1528926168.581094,
    "timed_out": true,
    "timeout": 20
}
```
