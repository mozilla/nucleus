import React, { useEffect, useState } from "react";
import ReactDOM from "react-dom/client";

function BugLink({ bug }) {
  if (bug) {
    return <a href={`https://bugzilla.mozilla.org/show_bug.cgi?id=${bug}`}>{bug}</a>;
  }
  return <p></p>;
}

function ReleaseSpecific({ note, removeNote }) {
  const makeReleaseSpecific = () => {
    const copy = window.mori.assoc(
      window.mori.dissoc(window.mori.js_to_clj(note), "id", "url", "releases"),
      "releases",
      [window.releaseApiUrl]
    );
    window.authPost(
      "/rna/notes/",
      JSON.stringify(window.mori.clj_to_js(copy)),
      () => removeNote()
    );
  };

  if (note.releases.length === 1) {
    return <p>Yes</p>;
  }
  return <input type="button" value="Make release-specific" onClick={makeReleaseSpecific} />;
}

function NoteRow({ note, removeNote }) {
  return (
    <tr>
      <td><a href={`/admin/rna/note/${note.id}/`}>Edit</a></td>
      <td>{note.is_known_issue && note.is_known_issue !== window.releaseApiUrl ? "Known issue" : note.tag}</td>
      <td dangerouslySetInnerHTML={{ __html: window.converter.makeHtml(note.note) }} />
      <td><BugLink bug={note.bug} /></td>
      <td>{note.sort_num}</td>
      <td><ReleaseSpecific note={note} removeNote={() => removeNote(note)} /></td>
      <td><input type="button" value="Remove" onClick={() => removeNote(note)} /></td>
    </tr>
  );
}

function NoteRows({ data, removeNote }) {
  return (
    <tbody>
      {data.map((note, index) => (
        <NoteRow key={index} note={note} removeNote={removeNote} />
      ))}
    </tbody>
  );
}

function NoteHeader({ data }) {
  return (
    <thead>
      <tr>
        {data.map((header, index) => (
          <th key={index}>{header}</th>
        ))}
      </tr>
    </thead>
  );
}

function NoteTable({ url }) {
  const [data, setData] = useState([]);

  const getNotes = () => {
    window.$.ajax({
      url,
      success: (notes) => setData(notes),
      error: (jqXHR, textStatus, errorThrown) => {
        alert(`Unable to get notes: ${jqXHR.status} ${textStatus} ${errorThrown}`);
      }
    });
  };

  const addNote = (id) => {
    window.$.ajax({
      url: `/rna/notes/${id}/`,
      success: (note) => {
        const releases = JSON.stringify({ releases: [...note.releases, window.releaseApiUrl] });
        window.authPatch(note.url, releases, getNotes);
      }
    });
  };

  const removeNote = (note) => {
    const releases = JSON.stringify({
      releases: note.releases.filter((url) => url !== window.releaseApiUrl),
    });
    window.authPatch(note.url, releases, getNotes);
  };

  useEffect(() => {
    getNotes();

    const origLookup = window.dismissRelatedLookupPopup;
    window.dismissRelatedLookupPopup = (win, chosenId) => {
      addNote(chosenId);
      origLookup(win, chosenId);
    };

    const origAddAnother = window.dismissAddAnotherPopup;
    window.dismissAddAnotherPopup = (win, newId, newRepr) => {
      addNote(newId);
      origAddAnother(win, newId, newRepr);
    };
  }, []);

  const headers = ["Edit", "Tag/Known issue", "Note", "Bug", "Sort num", "Release-specific", "Remove"];

  return (
    <table>
      <NoteHeader data={headers} />
      <NoteRows data={data} removeNote={removeNote} />
    </table>
  );
}

const rootEl = document.getElementById("note-table");
if (rootEl) {
  const root = ReactDOM.createRoot(rootEl);
  root.render(<NoteTable url={window.notesApiUrl} />);
}
