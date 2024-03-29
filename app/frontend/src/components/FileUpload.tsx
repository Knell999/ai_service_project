/**
 * FileUpload is a React component for uploading files.
 * It uses the react-dropzone library to provide drag-and-drop file upload functionality.
 *
 * State:
 * - file: The file to be uploaded. Initially null.
 *
 * Callbacks:
 * - onDrop: Called when a file is dropped into the dropzone. It updates the file state with the dropped file.
 *
 * Methods:
 * - handleSendFile: Called when the "Send File" button is clicked. If a file has been selected, it logs the file name to the console.
 *   The actual sending logic should be implemented here.
 *
 * Render:
 * - A div with class "upload-container", which contains the dropzone and the buttons.
 * - The dropzone is a div that allows files to be dropped into it. It also contains an input element for file selection.
 * - The "Select File" button triggers a click on the file input element when clicked, opening the file selection dialog.
 * - The "Send File" button calls handleSendFile when clicked.
 */
import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';

const FileUpload = () => {
  const [file, setFile] = useState<File | null>(null);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    // Assuming only one file is accepted
    setFile(acceptedFiles[0]);
  }, []);

  const { getRootProps, getInputProps } = useDropzone({ onDrop });

  const handleSendFile = () => {
    if (file) {
      console.log('Sending file:', file.name);
      // Implement the sending logic here
    }
  };

  return (
    <div className="upload-container" style={{ textAlign: 'center', padding: '50px' }}>
      <div {...getRootProps({ className: 'dropzone' })} style={{ border: '2px dashed gray', padding: '20px', cursor: 'pointer' }}>
        <input {...getInputProps()} />
        <p>Drag 'n' drop your file here, or click to select file</p>
      </div>
      <button onClick={() => (document.querySelector('input[type=file]') as HTMLInputElement)?.click()} style={{ marginTop: '10px' }}>
        Select File
      </button>
      <button onClick={handleSendFile} style={{ marginLeft: '10px' }}>
        Send File
      </button>
    </div>
  );
};

export default FileUpload;
