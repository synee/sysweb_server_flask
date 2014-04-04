$(()->
    Terminal = window.Terminal = Events.extend

    # 已经输入
        hasInputs: []
    # 当前输入
        currentInput: 0

        currentDir: "/"

        template: """
                    <div id='terminal' style=' font-family: monospace; font-size: 12px;'>
                        <div id='terminal_output'></div>
                        <div id='terminal_input' style='margin-bottom: 250px; clear: both;'>
                            <span id='terminal_path' style='color: #f8c; display: inline-block; float: left; line-height: 19px; padding: 0 6px 0 0;'>#{@currentDir} ~#</span>
                            <input style='margin: 0;color: #0fc; background: #333; border: 0; outline: none; width: 80%; float: left; font-family: monospace;padding-top: 2px; '/>
                        </div>
                    </div>
                  """
        style:
            position: "fixed", top: 0, left: 0, width: "100%", height: "100%", padding: "10px", background: "#333", color: "#0fc", overflow: "auto"

        $: (selector)->
            @$el.find.apply(@$el, arguments)

    # 前一个输入
        prevInput: ->
            @currentInput = @currentInput - 1
            if @currentInput < 0
                @currentInput = 0
            if(@hasInputs[@currentInput])
                @$input.val(@hasInputs[@currentInput])
                @$input.focus()
                @$input[0].selectionEnd = @$input.val().length
                return false
            else
                @currentInput = @hasInputs.length
                @$input.val("")

    # 后一个输入
        nextInput: ->
            @currentInput = @currentInput + 1
            if(@hasInputs[@currentInput] == undefined)
                @$input.val(@hasInputs[@currentInput])
                @$input.focus()
                @$input[0].selectionEnd = @$input.val().length
                return false
            else
                @currentInput = @hasInputs.length
                @$input.val("")

    # 输出 Element
        outputEl: (message) ->
            $("""<div class='output_line' style='font-family: monospace; font-size: 12px; padding: 2px 0;'></div>""").append(message)

    # 输出
        output: (message = '') ->
            $output = @outputEl(message)
            @$outputBox.append($output)
            @goon()
            $output

    # 输出错误
        outputError: (message = '')->
            @output().append($("<span style='padding: 5px 20px; color: #f66;'>#{message}</span>"))

    # 提交命令
        commit: (line = @line = @$input.val())->
            $o = @output()
            $o.append($("<span style='padding: 5px 5px 5px 0px; color: #f8c;'>#{@$('#terminal_path').text()}</span>"))
            $o.append($("<pre style='padding: 3px 5px 3px 2px; display: inline;'>#{$("<div/>").text(line).html()}</pre>"))
            if @$input.val()
                @hasInputs[@hasInputs.length] = @$input.val()
            @$input.val("").hide()
            @$("#terminal_path").text("")
            if (!line.trim())
                return @goon()
            @execute(line)

    # getParam
        getParam: (name) ->
            args = @line.split(/\s+/)
            if(args.indexOf(name) >= 0)
                return args[args.indexOf(name) + 1]
            else
                return undefined

    # 执行命令
        execute: (line)->
            argArr = line.split(/\s+/)
            fnName = argArr[0]
            fn = (Terminal.commandFunctions)[fnName]
            if (fn) fn.apply(@, [line, argArr.slice(1)].concat(argArr.slice(1)))
            else @output().append($("""<span style='padding: 5px 20px; color: #f66;'>No Such command: \" #{fnName} \"</span>"""))

    # 命令结束， 继续
        goon: ()->
            @$("#terminal_path").text("Sysweb:#{@currentDir}  #{if Sysweb.User.currentUser && Sysweb.User.currentUser.username then Sysweb.User.currentUser.username else 'Anonymous'}$")
            @$input.val("").show().focus()
            @$el.animate({ scrollTop: @$("#terminal_output").height()}, 50)
            @currentInput = @hasInputs.length

        getOpreatePath: (path)->
            cDir = @currentDir.substr(0, @currentDir.lastIndexOf("/"))
            path = path.replace("//", "/") while path.indexOf("//") >= 0
            if (path.indexOf("..") == 0)
                cDir = cDir.substr(0, cDir.lastIndexOf("/"))
                path = path.replace("..", "")
                if(path.indexOf("/") == 0)
                    path = path.substr(1)
            if (path.indexOf(".") == 0)
                path = path.substr(1)
                if(path.indexOf("/") == 0)
                    path = path.substr(1)
            if (path.indexOf("/") == 0)
                cDir = ""
            path = cDir + "/" + path
            path = path.substr(0, path.length - 1) while path.lastIndexOf("/") == path.length - 1 && path.length > 0
            path = path.replace("//", "/") while path.indexOf("//") >= 0
            return path

        initialize: (@args = {}
                     @template = @args.template || @template
                     @style = @args.style || @style)->
            $("#terminal").remove() if $("#terminal").length > 0
            @$el = $(@template).css(@style)
            $("body").append(@$el)
            @$outputBox = @$("#terminal_output")
            @$input = @$("#terminal_input input")
            @initHotkey()
            @initEvents()
            @initCommands()
            @goon()

        initHotkey: ->
            KeyBoardMaps.register("ctrl+c", =>
                @commit('')
                @goon()
            )

        addHotKey: (keyCombe, callback)->
            KeyBoardMaps.register(keyCombe, =>
                callback.apply(@, arguments))


        initEvents: ->
            @$el.on("click", =>
                @$input.focus())
            @$input.on("keydown", (e)=>
                @keyBoardListener(e))
            Sysweb.User.on("logined", @goon, @)
            Sysweb.User.on("forbidden", @outputError("Command forbidden, you have to log in."), @)
            Sysweb.fs.on("fserror", (result)=>
                @outputError(result.message))

        initCommands: ->

        keyBoardListener: (e)->
            if(e.keyCode == 13)
                return @commit()
            if(e.keyCode == 38)
                return @prevInput()
            if(e.keyCode == 40)
                return @nextInput()


    Sysweb.Applications.set("terminal", Terminal)

    Terminal.getInstance = (args)->
        if (!Terminal.instance)
            Terminal.instance = new Terminal(args)
        Terminal.instance.$("#terminal_input input").focus()
        return Terminal.instance


    # 添加命令
    Terminal.addCommandFunction = (name, fn = (args)->)->
        Terminal.commandFunctions[name] = fn
        Terminal.commandNames = Terminal.commandNames.filter((commandName)->
            commandName != name)
        Terminal.commandNames[Terminal.commandNames.length] = name

    Terminal.commandNames =
        [ "pwd", "cd", "ls", "touch", "stat", "read", "write", "append", "echo", "mkdir", "rm", "cp", "mv", "head",
          "tail"]

    # Terminal 命令
    Terminal.commandFunctions =
        pwd: ()->
            @output(@currentDir)
            @goon()

        cd: (line, args, path = '.')->
            path = @getOpreatePath(path) + "/"
            Sysweb.fs.cd(path).done (result)=>
                if(result.directory)
                    @currentDir = path
                @goon()

        ls: (line, args, path = ".")->
            Sysweb.fs.ls(@getOpreatePath(path)).done (result)=>
                $o = @output()
                $o.append($("<span style='padding: 5px 20px; color: #{if item.file then "#f99" else "#99f"}'>#{item.name}</span>")) for item in result.list

        touch: (line, args, path = ".")->
            if(args.length < 1)
                return @outputError("Missing parameters")
            path = @getOpreatePath(path)
            Sysweb.fs.touch(path).done (result)=>
                if(result.exists)
                    @goon()

        stat: (line, args, path = @currentDir)->
            Sysweb.fs.stat(@getOpreatePath(path)).done (result)=>
                $table = $("<table/>")
                @output($table)
                for key, value of result
                    if key == "modify"
                        value = new Date(value)
                    if key == "create"
                        value = new Date(value)
                    $table.append $("<tr/>").append($("<td style='padding: 2px 5px;'>#{key}</td>")).append($("<td style='padding: 2px 5px;'>#{value}</td>"))

        read: (line, args, path)->
            self = @
            if(args.length < 1)
                @outputError("Missing parameters")
                return @goon()
            path = self.getOpreatePath(path)
            Sysweb.fs.read(path).done (result)=>
                if(result.exists)
                    @output().append($("<pre style='padding: 5px 20px; color: #fff;'>#{$("<div/>").text(result.text).html()}</pre>"))

        write: (line, args, path)->
            self = @
            if(args.length < 2)
                return @outputError("Missing parameters")
            text = line.substr(line.indexOf(path) + path.length)
            path = self.getOpreatePath(path)
            Sysweb.fs.write(path, text).done (result)->
                if(result.exists)
                    @output().append($("<pre style='padding: 5px 20px; color: #fff;'>#{$("<div/>").text(result.text).html()}</pre>"))

        append: (line, args, path)->
            self = @
            if(args.length < 2)
                return @output(line.replace("echo", "").trim())
            text = line.substr(line.indexOf(path) + path.length)
            path = self.getOpreatePath(path)
            Sysweb.fs.append(path, text).done (result)->
                if(result.exists)
                    @output().append($("<pre style='padding: 5px 20px; color: #fff;'>#{$("<div/>").text(result.text).html()}</pre>"))

        echo: (line, args)->
            if(args.length < 3 || args[args.length - 2] != ">>")
                return @output(line.replace("echo", "").trim())

            path = @getOpreatePath(args[args.length - 1])
            text = line.substr(5, line.lastIndexOf(">>") - 5).trim()
            if(text.indexOf("\"") == 0)
                text = text.substr(1)
            if(text.lastIndexOf("\"") == text.length - 1)
                text = text.substr(0, text.length - 1)
            Sysweb.fs.echo(path, text).done (result)=>
                if(result.exists)
                    @output().append($("<pre style='padding: 5px 20px; color: #fff;'>#{$("<div/>").text(result.text).html()}</pre>"))

        mkdir: (line, args, path = args[0] || "")->
            self = @
            path = self.getOpreatePath(path)
            Sysweb.fs.mkdir(path).done (result)->
                if(!result.error)
                    self.goon()

        rm: (line, args, path)->
            path = @getOpreatePath(path)
            Sysweb.fs.rm(path).done (result)=>
                if !result.exists
                    @outputError("cp failed!")
                else
                    @output("mv success!")

        cp: (line, args, source, dest)->
            if (args.length < 2)
                return @output().append($("<span style='padding: 5px 20px; color: #f66;'>Args error</span>"))
            source = @getOpreatePath(source)
            dest = @getOpreatePath(dest)
            Sysweb.fs.cp(source, dest).done (result)=>
                if result.error
                    @outputError("cp failed!")
                else
                    @output("cp success!")

        mv: (line, args, source = args[0], dest = args[1])->
            if (!source || !dest)
                return @outputError("arguments provided is not enough")
            source = @getOpreatePath(source)
            dest = @getOpreatePath(dest)
            Sysweb.fs.mv(source, dest).done (result)=>
                if result.error
                    @outputError("mv failed!")
                else
                    @output("mv success!")

        head: (line, args, path, start, stop)->
            Sysweb.fs.head(@getOpreatePath(path), start, stop).done (result)=>
                if(result.text)
                    @output().append($("<pre style='padding: 5px 20px; color: #fff;'>#{$("<div/>").text(result.text).html()}</pre>"))

        tail: (line, args, path = args[0], start, stop)->
            Sysweb.fs.tail(@getOpreatePath(path), start, stop).done (result)=>
                if(result.text)
                    @output().append($("<pre style='padding: 5px 20px; color: #fff;'>#{$("<div/>").text(result.text).html()}</pre>"))
                else
                    @outputError("Tail failed!")

    Terminal.getInstance()

    # Login
    Terminal.addCommandFunction "login", ()->
        email = @getParam("-e")
        password = @getParam("-p")
        if(email && password)
            Sysweb.User.login({email: email, password: password}).done (result)=>
                if(result.user)
                    Sysweb.User.currentUser = result.user
                    Terminal.getInstance().currentDir = "/"
                    @output().append($("<span style='padding: 5px 20px; color: #6f6;'>has login as [#{result.user.username}]</span>"))
                else
                    @outputError("Login Failed")
        else
            @outputError("Email and password are needed.")

    Terminal.addCommandFunction "logout", ()->
        $.get("/logout").done(=>
            window.location.reload()).fail(=>
            @outputError("Log out Error"))

    # Register
    Terminal.addCommandFunction "register", (line, args)->
        email = @getParam("-e")
        password = @getParam("-p")
        if(email && password)
            Sysweb.User.register({email: email, password: password }).done (result)=>
                if (result.error)
                    @outputError(result.message)
                else
                    @output("We have send you an email which to active your account.")
        else
            @outputError('Email and password are needed.')

    Terminal.addCommandFunction "help", ()->
        window.open("https://github.com/synee/sysweb_server_flask/blob/master/static/README.md", "_blank")
        @goon()

    Terminal.addCommandFunction "export", (line, args, path, option)->
        if !path
            return @outputError("Missing path")

        path = @getOpreatePath(path)
        if option == "delete"
            return Sysweb.Env.deleteExport(path, =>
                @output("Export delete success"))

        Sysweb.fs.stat(path).done (result)=>
            if result.absolutePath
                Sysweb.Env.export(result.absolutePath, =>
                    @output("Export success"))
            else @outputError("No Such File")

    Terminal.addCommandFunction "commands", (line, args) ->
        $ul = $("<ul style='list-style-type: none; display: table;'/>")
        @output($ul)
        $ul.append($("<li style='float: left; padding-right: 20px;'>#{command}</li>")) for command in Terminal.commandNames

    Terminal.addCommandFunction "publish", (line, args, path, as, version = 0) ->
        Sysweb.Api.publish(path, as, version)
        @outputError("Not Finished")

    Terminal.addCommandFunction "install", (line, args, app, version = 0) ->
        Sysweb.Api.install(app, version)
        @outputError("Not Finished")
)



