// Generated by CoffeeScript 1.6.3
(function() {
  $(function() {
    var Terminal;
    Terminal = window.Terminal = Events.extend({
      hasInputs: [],
      currentInput: 0,
      currentDir: "/",
      template: "<div id='terminal' style=' font-family: monospace; font-size: 12px;'>\n    <div id='terminal_output'></div>\n    <div id='terminal_input' style='margin-bottom: 250px; clear: both;'>\n        <span id='terminal_path' style='color: #f8c; display: inline-block; float: left; line-height: 19px; padding: 0 6px 0 0;'>" + this.currentDir + " ~#</span>\n        <input style='margin: 0;color: #0fc; background: #333; border: 0; outline: none; width: 80%; float: left; font-family: monospace;padding-top: 2px; '/>\n    </div>\n</div>",
      style: {
        position: "fixed",
        top: 0,
        left: 0,
        width: "100%",
        height: "100%",
        padding: "10px",
        background: "#333",
        color: "#0fc",
        overflow: "auto"
      },
      $: function(selector) {
        return this.$el.find.apply(this.$el, arguments);
      },
      atInput: function(index) {
        var value;
        if (index < 0) {
          index = 0;
        }
        if (index >= this.hasInputs.length) {
          index = this.hasInputs.length;
        }
        value = this.hasInputs[index] || '';
        this.$input.val(value);
        this.$input.focus();
        this.$input[0].selectionEnd = this.$input.val().length;
        this.currentInput = index;
        return false;
      },
      prevInput: function() {
        return this.atInput(this.currentInput - 1);
      },
      nextInput: function() {
        return this.atInput(this.currentInput + 1);
      },
      outputEl: function(message) {
        return $("<div class='output_line' style='font-family: monospace; font-size: 12px; padding: 2px 0;'></div>").append(message);
      },
      output: function(message) {
        var $output;
        if (message == null) {
          message = '';
        }
        $output = this.outputEl(message);
        this.$outputBox.append($output);
        this.goon();
        return $output;
      },
      outputError: function(message) {
        if (message == null) {
          message = '';
        }
        return this.output().append($("<span style='padding: 5px 20px; color: #f66;'>" + message + "</span>"));
      },
      commit: function(line) {
        var $o;
        if (line == null) {
          line = this.line = this.$input.val();
        }
        $o = this.output();
        $o.append($("<span style='padding: 5px 5px 5px 0px; color: #f8c;'>" + (this.$('#terminal_path').text()) + "</span>"));
        $o.append($("<pre style='padding: 3px 5px 3px 2px; display: inline;'>" + ($("<div/>").text(line).html()) + "</pre>"));
        if (line) {
          this.hasInputs[this.hasInputs.length] = line;
        } else {
          return this.goon();
        }
        this.$input.val("").hide();
        this.$("#terminal_path").text("");
        if (!line.trim()) {
          return this.goon();
        }
        return this.execute(line);
      },
      getParam: function(name) {
        var args;
        args = this.line.split(/\s+/);
        if (args.indexOf(name) >= 0) {
          return args[args.indexOf(name) + 1];
        } else {
          return void 0;
        }
      },
      execute: function(line) {
        var argArr, fn, fnName;
        argArr = line.split(/\s+/);
        fnName = argArr[0];
        fn = Terminal.commandFunctions[fnName];
        if (fn) {
          return fn.apply(this, [line, argArr.slice(1)].concat(argArr.slice(1)));
        } else {
          return this.output().append($("<span style='padding: 5px 20px; color: #f66;'>No Such command: \" " + fnName + " \"</span>"));
        }
      },
      goon: function() {
        this.$("#terminal_path").text("Sysweb:" + this.currentDir + "  " + (Sysweb.User.currentUser && Sysweb.User.currentUser.username ? Sysweb.User.currentUser.username : 'Anonymous') + "$");
        this.$input.val("").show().focus().width(this.$("#terminal_input").width() - this.$("#terminal_path").width() - 10);
        this.$el.animate({
          scrollTop: this.$("#terminal_output").height()
        }, 50);
        return this.currentInput = this.hasInputs.length;
      },
      getOpreatePath: function(path) {
        var cDir;
        if (path == null) {
          path = path || "";
        }
        cDir = this.currentDir.substr(0, this.currentDir.lastIndexOf("/"));
        while (path.indexOf("//") >= 0) {
          path = path.replace("//", "/");
        }
        if (path.indexOf("..") === 0) {
          cDir = cDir.substr(0, cDir.lastIndexOf("/"));
          path = path.replace("..", "");
          if (path.indexOf("/") === 0) {
            path = path.substr(1);
          }
        }
        if (path.indexOf(".") === 0) {
          path = path.substr(1);
          if (path.indexOf("/") === 0) {
            path = path.substr(1);
          }
        }
        if (path.indexOf("/") === 0) {
          cDir = "";
        }
        path = cDir + "/" + path;
        while (path.lastIndexOf("/") === path.length - 1 && path.length > 0) {
          path = path.substr(0, path.length - 1);
        }
        while (path.indexOf("//") >= 0) {
          path = path.replace("//", "/");
        }
        return path;
      },
      initialize: function(args, template, style) {
        this.args = args != null ? args : {};
        this.template = template != null ? template : this.args.template || this.template;
        this.style = style != null ? style : this.args.style || this.style;
        if ($("#terminal").length > 0) {
          $("#terminal").remove();
        }
        this.$el = $(this.template).css(this.style);
        $("body").append(this.$el);
        this.$outputBox = this.$("#terminal_output");
        this.$input = this.$("#terminal_input input");
        this.initHotkey();
        this.initEvents();
        this.initCommands();
        return this.goon();
      },
      initHotkey: function() {
        var _this = this;
        return KeyBoardMaps.register("ctrl+c", function() {
          _this.commit('');
          return _this.goon();
        });
      },
      addHotKey: function(keyCombe, callback) {
        var _this = this;
        return KeyBoardMaps.register(keyCombe, function() {
          return callback.apply(_this, arguments);
        });
      },
      initEvents: function() {
        var _this = this;
        this.$el.on("click", function() {
          return _this.$input.focus();
        });
        this.$input.on("keydown", function(e) {
          return _this.keyBoardListener(e);
        });
        Sysweb.User.on("logined", this.goon, this);
        Sysweb.User.on("forbidden", function() {
          return _this.outputError("Command forbidden, you have to log in.");
        });
        return Sysweb.fs.on("fserror", function(result) {
          return _this.outputError(result.message);
        });
      },
      initCommands: function() {},
      keyBoardListener: function(e) {
        if (e.keyCode === 13) {
          return this.commit();
        }
        if (e.keyCode === 38) {
          return this.prevInput();
        }
        if (e.keyCode === 40) {
          return this.nextInput();
        }
      }
    });
    Sysweb.Applications.set("terminal", Terminal);
    Terminal.getInstance = function(args) {
      if (!Terminal.instance) {
        Terminal.instance = new Terminal(args);
      }
      Terminal.instance.$("#terminal_input input").focus();
      return Terminal.instance;
    };
    Terminal.addCommandFunction = function(name, fn) {
      if (fn == null) {
        fn = function(args) {};
      }
      Terminal.commandFunctions[name] = fn;
      Terminal.commandNames = Terminal.commandNames.filter(function(commandName) {
        return commandName !== name;
      });
      return Terminal.commandNames[Terminal.commandNames.length] = name;
    };
    Terminal.commandNames = ["pwd", "cd", "ls", "touch", "stat", "read", "write", "append", "echo", "mkdir", "rm", "cp", "mv", "head", "tail"];
    Terminal.commandFunctions = {
      pwd: function() {
        this.output(this.currentDir);
        return this.goon();
      },
      cd: function(line, args, path) {
        var _this = this;
        if (path == null) {
          path = '.';
        }
        path = this.getOpreatePath(path) + "/";
        return Sysweb.fs.cd(path).done(function(result) {
          if (result.directory) {
            _this.currentDir = path;
          }
          return _this.goon();
        });
      },
      ls: function(line, args, path) {
        var _this = this;
        if (path == null) {
          path = ".";
        }
        return Sysweb.fs.ls(this.getOpreatePath(path)).done(function(result) {
          var $o, item, _i, _len, _ref, _results;
          $o = _this.output();
          if (result && result.list) {
            _ref = result.list;
            _results = [];
            for (_i = 0, _len = _ref.length; _i < _len; _i++) {
              item = _ref[_i];
              _results.push($o.append($("<span style='padding: 5px 20px; color: " + (item.file ? "#f99" : "#99f") + "'>" + item.name + "</span>")));
            }
            return _results;
          }
        });
      },
      touch: function(line, args, path) {
        var _this = this;
        if (path == null) {
          path = ".";
        }
        if (args.length < 1) {
          return this.outputError("Missing parameters");
        }
        path = this.getOpreatePath(path);
        return Sysweb.fs.touch(path).done(function(result) {
          if (result.exists) {
            return _this.goon();
          }
        });
      },
      stat: function(line, args, path) {
        var _this = this;
        if (path == null) {
          path = this.currentDir;
        }
        return Sysweb.fs.stat(this.getOpreatePath(path)).done(function(result) {
          var $table, key, value, _results;
          $table = $("<table/>");
          _this.output($table);
          _results = [];
          for (key in result) {
            value = result[key];
            if (key === "modify") {
              value = new Date(value);
            }
            if (key === "create") {
              value = new Date(value);
            }
            _results.push($table.append($("<tr/>").append($("<td style='padding: 2px 5px;'>" + key + "</td>")).append($("<td style='padding: 2px 5px;'>" + value + "</td>"))));
          }
          return _results;
        });
      },
      read: function(line, args, path) {
        var self,
          _this = this;
        self = this;
        if (args.length < 1) {
          this.outputError("Missing parameters");
          return this.goon();
        }
        path = self.getOpreatePath(path);
        return Sysweb.fs.read(path).done(function(result) {
          if (result.exists) {
            return _this.output().append($("<pre style='padding: 5px 20px; color: #fff;'>" + ($("<div/>").text(result.text).html()) + "</pre>"));
          }
        });
      },
      write: function(line, args, path) {
        var self, text;
        self = this;
        if (args.length < 2) {
          return this.outputError("Missing parameters");
        }
        text = line.substr(line.indexOf(path) + path.length);
        path = self.getOpreatePath(path);
        return Sysweb.fs.write(path, text).done(function(result) {
          if (result.exists) {
            return this.output().append($("<pre style='padding: 5px 20px; color: #fff;'>" + ($("<div/>").text(result.text).html()) + "</pre>"));
          }
        });
      },
      append: function(line, args, path) {
        var self, text;
        self = this;
        if (args.length < 2) {
          return this.output(line.replace("echo", "").trim());
        }
        text = line.substr(line.indexOf(path) + path.length);
        path = self.getOpreatePath(path);
        return Sysweb.fs.append(path, text).done(function(result) {
          if (result.exists) {
            return this.output().append($("<pre style='padding: 5px 20px; color: #fff;'>" + ($("<div/>").text(result.text).html()) + "</pre>"));
          }
        });
      },
      echo: function(line, args) {
        var path, text,
          _this = this;
        if (args.length < 3 || args[args.length - 2] !== ">>") {
          return this.output(line.replace("echo", "").trim());
        }
        path = this.getOpreatePath(args[args.length - 1]);
        text = line.substr(5, line.lastIndexOf(">>") - 5).trim();
        if (text.indexOf("\"") === 0) {
          text = text.substr(1);
        }
        if (text.lastIndexOf("\"") === text.length - 1) {
          text = text.substr(0, text.length - 1);
        }
        return Sysweb.fs.echo(path, text).done(function(result) {
          if (result.exists) {
            return _this.output().append($("<pre style='padding: 5px 20px; color: #fff;'>" + ($("<div/>").text(result.text).html()) + "</pre>"));
          }
        });
      },
      mkdir: function(line, args, path) {
        var self;
        if (path == null) {
          path = args[0] || "";
        }
        self = this;
        path = self.getOpreatePath(path);
        return Sysweb.fs.mkdir(path).done(function(result) {
          if (!result.error) {
            return self.goon();
          }
        });
      },
      rm: function(line, args, path) {
        var _this = this;
        path = this.getOpreatePath(path);
        return Sysweb.fs.rm(path).done(function(result) {
          if (!result.exists) {
            return _this.outputError("cp failed!");
          } else {
            return _this.output("mv success!");
          }
        });
      },
      cp: function(line, args, source, dest) {
        var _this = this;
        if (args.length < 2) {
          return this.output().append($("<span style='padding: 5px 20px; color: #f66;'>Args error</span>"));
        }
        source = this.getOpreatePath(source);
        dest = this.getOpreatePath(dest);
        return Sysweb.fs.cp(source, dest).done(function(result) {
          if (result.error) {
            return _this.outputError("cp failed!");
          } else {
            return _this.output("cp success!");
          }
        });
      },
      mv: function(line, args, source, dest) {
        var _this = this;
        if (source == null) {
          source = args[0];
        }
        if (dest == null) {
          dest = args[1];
        }
        if (!source || !dest) {
          return this.outputError("arguments provided is not enough");
        }
        source = this.getOpreatePath(source);
        dest = this.getOpreatePath(dest);
        return Sysweb.fs.mv(source, dest).done(function(result) {
          if (result.error) {
            return _this.outputError("mv failed!");
          } else {
            return _this.output("mv success!");
          }
        });
      },
      head: function(line, args, path, start, stop) {
        var _this = this;
        return Sysweb.fs.head(this.getOpreatePath(path), start, stop).done(function(result) {
          if (result.text) {
            return _this.output().append($("<pre style='padding: 5px 20px; color: #fff;'>" + ($("<div/>").text(result.text).html()) + "</pre>"));
          }
        });
      },
      tail: function(line, args, path, start, stop) {
        var _this = this;
        if (path == null) {
          path = args[0];
        }
        return Sysweb.fs.tail(this.getOpreatePath(path), start, stop).done(function(result) {
          if (result.text) {
            return _this.output().append($("<pre style='padding: 5px 20px; color: #fff;'>" + ($("<div/>").text(result.text).html()) + "</pre>"));
          } else {
            return _this.outputError("Tail failed!");
          }
        });
      }
    };
    Terminal.getInstance();
    Terminal.addCommandFunction("login", function() {
      var email, password,
        _this = this;
      email = this.getParam("-e");
      password = this.getParam("-p");
      if (email && password) {
        return Sysweb.User.login({
          email: email,
          password: password
        }).done(function(result) {
          if (result.user) {
            Sysweb.User.currentUser = result.user;
            Terminal.getInstance().currentDir = "/";
            return _this.output().append($("<span style='padding: 5px 20px; color: #6f6;'>has login as [" + result.user.username + "]</span>"));
          } else {
            return _this.outputError("Login Failed");
          }
        });
      } else {
        return this.outputError("Email and password are needed.");
      }
    });
    Terminal.addCommandFunction("logout", function() {
      var _this = this;
      return $.get("/logout").done(function() {
        return window.location.reload();
      }).fail(function() {
        return _this.outputError("Log out Error");
      });
    });
    Terminal.addCommandFunction("register", function(line, args) {
      var email, password,
        _this = this;
      email = this.getParam("-e");
      password = this.getParam("-p");
      if (email && password) {
        return Sysweb.User.register({
          email: email,
          password: password
        }).done(function(result) {
          if (result.error) {
            return _this.outputError(result.message);
          } else {
            return _this.output("We have send you an email which to active your account.");
          }
        });
      } else {
        return this.outputError('Email and password are needed.');
      }
    });
    Terminal.addCommandFunction("help", function() {
      window.open("https://github.com/synee/sysweb_server_flask/blob/master/static/README.md", "_blank");
      return this.goon();
    });
    Terminal.addCommandFunction("export", function(line, args, path, option) {
      var _this = this;
      if (!path) {
        return this.outputError("Missing path");
      }
      path = this.getOpreatePath(path);
      if (option === "delete") {
        return Sysweb.Env.deleteExport(path, function() {
          return _this.output("Export delete success");
        });
      }
      return Sysweb.fs.stat(path).done(function(result) {
        if (result.absolutePath) {
          return Sysweb.Env["export"](result.absolutePath, function() {
            return _this.output("Export success");
          });
        } else {
          return _this.outputError("No Such File");
        }
      });
    });
    Terminal.addCommandFunction("commands", function(line, args) {
      var $ul, command, _i, _len, _ref, _results;
      $ul = $("<ul style='list-style-type: none; display: table;'/>");
      this.output($ul);
      _ref = Terminal.commandNames;
      _results = [];
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        command = _ref[_i];
        _results.push($ul.append($("<li style='float: left; padding-right: 20px;'>" + command + "</li>")));
      }
      return _results;
    });
    Terminal.addCommandFunction("publish", function(line, args, path, as, version) {
      if (version == null) {
        version = 0;
      }
      Sysweb.Api.publish(path, as, version);
      return this.outputError("Not Finished");
    });
    return Terminal.addCommandFunction("install", function(line, args, app, version) {
      if (version == null) {
        version = 0;
      }
      Sysweb.Api.install(app, version);
      return this.outputError("Not Finished");
    });
  });

}).call(this);
