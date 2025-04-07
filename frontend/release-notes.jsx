import React, { useEffect, useState } from "react";
import ReactDOM from "react-dom/client";
import { authPost } from "./utils";

function BugLink({ bug }) {
  if (bug) {
    return <a href={`https://bugzilla.mozilla.org/show_bug.cgi?id=${bug}`}>{bug}</a>;
  }
  return <p></p>;
}

function ReleaseSpecific({ note, removeNote, releaseApiUrl }) {
  const makeReleaseSpecific = () => {
    const { id, url, releases, ...rest } = note;
    const copy = {
      ...rest,
      releases: [releaseApiUrl]
    };
    const body = JSON.stringify(copy);

    authPost("/rna/notes/", body)
      .then(() => removeNote())
      .catch((err) => alert(err.message));
  };

  if (note.releases.length === 1) {
    return <p>Yes</p>;
  }
  return <input type="button" value="Make release-specific" onClick={makeReleaseSpecific} />;
}

function NoteRow({ note, removeNote, releaseApiUrl, converter }) {
  return (
    <tr>
      <td><a href={`/admin/rna/note/${note.id}/`}>Edit</a></td>
      <td>{note.is_known_issue && note.is_known_issue !== releaseApiUrl ? "Known issue" : note.tag}</td>
      <td dangerouslySetInnerHTML={{ __html: converter.makeHtml(note.note) }} />
      <td><BugLink bug={note.bug} /></td>
      <td>{note.sort_num}</td>
      <td><ReleaseSpecific note={note} removeNote={removeNote} releaseApiUrl={releaseApiUrl} /></td>
      <td><input type="button" value="Remove" onClick={() => removeNote(note)} /></td>
    </tr>
  );
}

function NoteRows({ data, removeNote, releaseApiUrl, converter }) {
  return (
    <tbody>
      {data.map((note, index) => (
        <NoteRow
          key={index}
          note={note}
          removeNote={removeNote}
          releaseApiUrl={releaseApiUrl}
          converter={converter}
        />
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

function NoteTable({ url, releaseApiUrl, converter }) {
  const [data, setData] = useState([]);

  const getNotes = () => {
    fetch(url)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP error ${res.status}`);
        return res.json();
      })
      .then(setData)
      .catch((err) => alert(`Unable to get notes: ${err.message}`));
  };

  const addNote = (id) => {
    fetch(`/rna/notes/${id}/`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP error ${res.status}`);
        return res.json();
      })
      .then((note) => {
        const releases = JSON.stringify({ releases: [...note.releases, releaseApiUrl] });
        authPost(note.url, releases, true).then(getNotes).catch(err => alert(err.message));
      })
      .catch((err) => alert(`Unable to add note: ${err.message}`));
  };

  const removeNote = (note) => {
    const releases = JSON.stringify({
      releases: note.releases.filter((url) => url !== releaseApiUrl),
    });
    authPost(note.url, releases, true).then(getNotes).catch(err => alert(err.message));
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
      <NoteRows
        data={data}
        removeNote={removeNote}
        releaseApiUrl={releaseApiUrl}
        converter={converter}
      />
    </table>
  );
}

const rootEl = document.getElementById("note-table");
if (rootEl) {
  const releaseId = rootEl.dataset.releaseid;
  const releaseApiUrl = `${window.location.origin}/rna/releases/${releaseId}/`;
  const notesApiUrl = `${releaseApiUrl}notes/`;
  const converter = new window.Markdown.Converter();

  const root = ReactDOM.createRoot(rootEl);
  root.render(<NoteTable url={notesApiUrl} releaseApiUrl={releaseApiUrl} converter={converter} />);
}
