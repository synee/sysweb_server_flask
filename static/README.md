sysweb_server
=============

Sysweb

## API

### auth

+ login
    * url:
        + /login
    * params:
        + username
        + password
    * return:
        + user object
+ register
    * url:
        + /register
    * params:
        + username
        + password
        + repasswd
    * return
        + user object
+ fetchme
    * url:
        + /user/current
    * return
        + user object

### fs
##### API
--------------
- cd
    * url:
        + /fs/cd
    * params:
        + path
    * return:
        + file object
- ls
    * url:
        + /fs/ls
    * params:
        + path
    * return:
        + file list
- cp
    * url:
        + /fs/cp
    * params:
        + source
        + dest
    * return:
        + source object
        + dest object
- mv
    * url:
        + /fs/mv
    * params:
        + source
        + dest
    * return:
        + source object
        + dest object
- mkdir
    * url:
        + /fs/mkdir
    * params:
        + path
    * return:
        + file object
- touch
    * url:
        + /fs/touch
    * params:
        + path
    * return:
        + file object
- echo
    * url:
        + /fs/echo
    * params:
        + path
        + text
    * return:
        + file object
- append
    * url:
        + /fs/append
    * params:
        + path
        + text
    * return:
        + file object
- write
    * url:
        + /fs/write
    * params:
        + path
        + text
    * return:
        + file object
- read
    * url:
        + /fs/read
    * params:
        + path
    * return:
        + file object with content text
- head
    * url:
        + /fs/head
    * params:
        + path
        + start
        + stop
    * return:
        + file object with headlines content text
- tail
    * url:
        + /fs/tail
    * params:
        + path
        + start
        + stop
    * return:
        + file object with taillines content text

##### API error
--------------
- bad request
    + code: 400
    + error: true
    + description: bad request, maybe some required params are not provide
- forbidden
    + code: 403
    + error: true
    + description: access forbidden, you have to login as correct account
- not exist
    + code: 404
    + error: true
    + description: what you access is not exist


#### Terminal
- add commands
    * example 1

        ``` shell
        export /app.js
        ```

        ``` javascript
        Terminal.addCommandFunction("export", function(line, args, path) { # line == export /app.js, args == ["/app.js"], path == args[0] == "/app.js"
          var self,
            _this = this;
          self = this;
          if (!path) {
            this.outputError("Missing path");
            return;
          }
          path = this.getOpreatePath(path);
          return Sysweb.fs.stat(path).done(function(result) {
            var newScript;
            if (result.error || !result.file) {
              _this.outputError("" + path + " should be a file");
              return _this.goon();
            }
            if (path === "/__sys.js") {
              _this.outputError("Can not export /__sys.js");
              _this.goon();
              return;
            }
            newScript = "document.getElementsByTagName('head')[0].appendChild(document.createElement('script')).setAttribute('src', '/sys_root/" + Sysweb.User.currentUser.username + path + "');";
            return Sysweb.fs.read("/__sys.js").done(function(result) {
              var text;
              text = result.text;
              text = text.replace(newScript, "");
              text += "\n" + newScript;
              return Sysweb.fs.write("/__sys.js", text).done(function() {
                return self.goon();
              });
            });
          });
        });
        ```

    * example 2

        ``` shell
        register -e one@example.com -p passwd
        ```

        ``` javascript
        Terminal.addCommandFunction("register", function(line, args) { # line == "register -e one@example.com -p passwd", args == ["-e", "one@example.com", "-p", "passwd"]
          var email, password, self;
          self = this;
          email = this.getParam("-e");
          password = this.getParam("-p");
          Sysweb.User.once("registerfailed", function() {
            return self.goon();
          });
          if (email && password) {
            Sysweb.User.register({
              email: email,
              password: password
            }).done(function(result) {
              if (result.error) {
                return terminal.outputError(result.message);
              } else {
                return terminal.output("We have send you an email which to active your account.");
              }
            });
          } else {
            terminal.outputError('Email and password are needed.');
          }
          return this.goon();
        });
        ```


