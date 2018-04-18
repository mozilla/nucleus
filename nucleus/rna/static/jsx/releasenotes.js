/** @jsx React.DOM */

;(function($, React, Markdown, mori) {
  'use strict';
  var authToken;
  var converter = new Markdown.Converter();
  var releaseId = $('#note-table').data('releaseid');
  var releaseApiUrl = window.location.origin + '/rna/releases/' + releaseId + '/';
  var notesApiUrl = releaseApiUrl + 'notes/';

  function authPost(url, data, callback, patchOverride) {
    var headers = {'Content-Type': 'application/json'};
    if(patchOverride) {
      headers['X-HTTP-Method-Override'] = 'PATCH';
    }
    function ajaxPost() {
      headers.Authorization = 'Token ' + authToken;
      $.ajax({
        url: url,
        method: 'POST',
        headers: headers,
        data: data,
        success: callback,
        error: function(jqXHR, textStatus, errorThrown) {
          alert('Unable to complete request: ' + jqXHR.status + ' ' + textStatus + ' ' + errorThrown);
        }
      });
    }

    if (authToken) {
      ajaxPost();
    } else {
      $.ajax({
        url: '/rna/auth_token/',
        success: function(d) {
          if (d.token) {
            authToken = d.token;
            ajaxPost();
          } else {
            alert('Unable to acquire authToken: response from server did not contain token');
          }
        },
        error: function(jqXHR, textStatus, errorThrown) {
          alert('Unable to acquire authToken: ' + jqXHR.status + ' ' + textStatus + ' ' + errorThrown);
        }

      });
    }
  }

  function authPatch(url, data, callback) {
    authPost(url, data, callback, true);
  }

  function bugUrl(bug) {
    return 'https://bugzilla.mozilla.org/show_bug.cgi?id=' + bug;
  }

  var BugLink = React.createClass({
    render: function() {
      if (this.props.bug) {
        return <a href={bugUrl(this.props.bug)}>{this.props.bug}</a>;
      }
      return <p></p>;
    }
  });


  function noteAdminUrl(noteId) {
    return '/admin/rna/note/' + noteId + '/';
  }

  function tagOrKnownIssue(note) {
    if(note.is_known_issue && note.is_known_issue != releaseApiUrl) {
      return 'Known issue';
    }
    return note.tag;
  }

  var ReleaseSpecific = React.createClass({
    makeReleaseSpecific: function() {
      var copy = mori.assoc(
          mori.dissoc(mori.js_to_clj(this.props.note), 'id', 'url', 'releases'),
          'releases', [releaseApiUrl]);
      authPost('/rna/notes/', JSON.stringify(mori.clj_to_js(copy)), function() {
        this.props.removeNote();
      }.bind(this));
    },
    render: function() {
      if(this.props.note.releases.length == 1) {
        return <p>Yes</p>;
      } else {
        return <input type="button" value="Make release-specific" onClick={this.makeReleaseSpecific} />;
      }
    }
  });

  var NoteRow = React.createClass({
    removeNote: function() {
      this.props.removeNote(this.props.note);
    },
    render: function() {
      var note = this.props.note;
      return (
        <tr>
          <td><a href={noteAdminUrl(note.id)}>Edit</a></td>
          <td>{tagOrKnownIssue(note)}</td>
          <td dangerouslySetInnerHTML={{__html: converter.makeHtml(note.note)}} />
          <td><BugLink bug={note.bug} /></td>
          <td>{note.sort_num}</td>
          <td><ReleaseSpecific note={note} removeNote={this.removeNote} /></td>
          <td><input type="button" value="Remove" onClick={this.removeNote} /></td>
        </tr>
      );
    }
  });

  var NoteRows = React.createClass({
    render: function() {
      var noteRows = this.props.data.map(function (note, index) {
        return <NoteRow key={index} note={note} removeNote={this.props.removeNote} />;
      }.bind(this));
      return <tbody>{noteRows}</tbody>;
    }
  });

  var NoteHeader = React.createClass({
    render: function() {
      var headers = this.props.data.map(function (header, index) {
        return <th key={index}>{header}</th>;
      });
      return (
        <thead>
          <tr>{headers}</tr>
        </thead>
      );
    }
  });

  var NoteTable = React.createClass({
    addNote: function(id) {
      $.ajax({
        url: '/rna/notes/' + id + '/',
        success: function(note) {
          var releases = JSON.stringify({releases: note.releases.concat(releaseApiUrl)});
          authPatch(note.url, releases, function() {
            this.getNotes(); 
          }.bind(this));
        }.bind(this)
      });
    },
    removeNote: function(note) {
      var releases = JSON.stringify({releases: note.releases.filter(function(releaseUrl) {
        return releaseUrl != releaseApiUrl;
      })});
      authPatch(note.url, releases, function() {
        this.getNotes(); 
      }.bind(this));
    },
    render: function() {
      var headers = ['Edit', 'Tag/Known issue', 'Note', 'Bug', 'Sort num', 'Release-specific', 'Remove'];
      return (
        <table>
          <NoteHeader data={headers} />
          <NoteRows data={this.state.data} removeNote={this.removeNote} />
        </table>
      );
    },
    getInitialState: function() {
      return {data: []};
    },
    getNotes: function() {
      $.ajax({
        url: this.props.url,
        success: function(data) {
          this.setState({data: data});
        }.bind(this),
        error: function(jqXHR, textStatus, errorThrown) {
          alert('Unable to get notes: ' + jqXHR.status + ' ' + textStatus + ' ' + errorThrown);
        }
      });
    },
    componentWillMount: function() {
      this.getNotes();

      var django_dismissRelatedLookupPopup = window.dismissRelatedLookupPopup;
      window.dismissRelatedLookupPopup = function(win, chosenId) {
        this.addNote(chosenId);
        django_dismissRelatedLookupPopup(win, chosenId);
      }.bind(this);

      var django_dismissAddAnotherPopup = window.dismissAddAnotherPopup;
      window.dismissAddAnotherPopup = function(win, newId, newRepr) {
        this.addNote(newId);
        django_dismissAddAnotherPopup(win, newId, newRepr);
      }.bind(this);
    }
  });

  React.renderComponent(
    <NoteTable url={notesApiUrl} />,
    document.getElementById('note-table')
  );
})(window.jQuery, window.React, window.Markdown, window.mori);
