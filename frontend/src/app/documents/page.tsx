// add a UI that shows a fake list of documents and an "Upload" button.

const DocumentsPage = () => {
    return (
        <div className="flex flex-col items-center w-full">
            <h1 className="text-2xl font-bold w-full">Documents</h1>
            <div className="flex flex-col items-center w-full mt-4">
                <div className="w-full">
                    <p>Documents</p>
                </div>
                <form className="w-full">
                    <input type="file" />
                    <button type="submit">Upload</button>
                </form>
            </div>
        </div>
    );
};

export default DocumentsPage;
