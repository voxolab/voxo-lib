
class FileStatus:
    Success = 1
    ExtensionNotAllowed = 2
    Error = 3
    ToDelete = 4
    Deleted = 5

    @staticmethod
    def to_dict():
        return {
            FileStatus.Success: 'Success',
            FileStatus.ExtensionNotAllowed: 'ExtensionNotAllowed',
            FileStatus.Error: 'Error',
            FileStatus.ToDelete: 'ToDelete',
            FileStatus.Deleted: 'Deleted'
            }

class DecodeStatus:
    Queued = 1
    Started = 2
    Segmentation = 3
    Transcription = 4
    Finished = 5
    Error = 6

    @staticmethod
    def from_string(string):
        inversed_dict = {v:k for k, v in DecodeStatus.to_dict().items()}
        return inversed_dict[string]

    @staticmethod
    def to_dict():
        return {
            DecodeStatus.Queued: 'Queued',
            DecodeStatus.Started: 'Started',
            DecodeStatus.Segmentation: 'Segmentation',
            DecodeStatus.Transcription: 'Transcription',
            DecodeStatus.Finished: 'Finished',
            DecodeStatus.Error: 'Error'
            }

class ProcessType:
    FullTranscription = 1
    FullPhoneTranscription = 2
    TranscriptionAlignment = 3
    FullEnglishTranscription = 4
    CustomModelTranscription = 5

    @staticmethod
    def to_dict():
        return {
            ProcessType.FullTranscription: 'Full transcription',
            ProcessType.FullPhoneTranscription: 'Full phone transcription',
            ProcessType.TranscriptionAlignment: 'Transcription alignment',
            ProcessType.FullEnglishTranscription: 'Full english transcription'
            ProcessType.CustomModelTranscription: 'Transcription with custom model'
            }

