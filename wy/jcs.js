const electron = require('electron');
const {
    webContents
} = require('electron');
const {
    session
} = require('electron');
const {
    dialog
} = require('electron');
const {
    autoUpdater
} = require('electron-updater');

const BrowserWindow = electron.BrowserWindow;
const Menu = electron.Menu;
const app = electron.app;
const path = require('path');
const ipc = require('electron').ipcMain;
let projectName = "jcw";
let projectIco = "ico_tph.ico";
let projectUrl = "https://dz.jchl.com/#/edfx-app-root/edfx-app-login";

let template = [{
    id: 1,
    label: '返回',
    click: function (item, focusedWindow) {
        if (focusedWindow) {
            focusedWindow.webContents.goBack()
        }
    }
}, {
    id: 2,
    label: '进度',
    click: function (item, focusedWindow) {
        if (focusedWindow) {
            win2 = {
            width: 700,
            height:500,

                 x:102,
                 y:193,
            title: '记录界面',movable:false,resizable:false,minimizable:false,closable:true,
                 alwaysOnTop:true,
            icon: projectIco,
            webPreferences: {
            webSecurity: false

        }};
        gzWindow = new BrowserWindow(win2);
        gzWindow.loadURL('D://electron_jcs/index.html');
        }
    }
}, {
    id: 3,
    label: '刷新',
    accelerator: 'F5',
    click: function (item, focusedWindow) {
        if (focusedWindow) {
            // 重载之后, 刷新并关闭所有的次要窗体
            if (focusedWindow.id === 1) {
                BrowserWindow.getAllWindows().forEach(function (win) {
                    if (win.id > 1) {
                        win.close()
                    }
                })
            }
            focusedWindow.reload()
        }
    }
}, {
    id: 4,
    label: '控制台',
    accelerator: 'F6',
    click: function (item, focusedWindow) {
        if (focusedWindow) {
            BrowserWindow.getFocusedWindow().webContents.openDevTools()
        }
    }
}];

function createWindow() {
    // 创建浏览器窗口。
    win = new BrowserWindow({
        width: 1300,
        height: 766,
        autoHideMenuBar: false,
        title: projectName,
        icon: projectIco,
        webPreferences: {
            webSecurity: false,
        }
    });

    win.webContents.on('crashed', function () {
        // storage.clear()
        console.log('cra')
    });

    win.webContents.on('unresponsive', function () {
        // storage.clear()
        console.log('unr')
    });

    win.webContents.on('closed', function () {
        // storage.clear()
        console.log('clo')
    });

    win.webContents.on('destroyed', function () {
        // storage.clear()
        console.log('des')
    });

    win.webContents.on('did-finish-load', (event, url,) => {
        win.webContents.executeJavaScript(`      
        var denglu = document.getElementsByTagName("button")[3];
        denglu.addEventListener('click', denglu_msg, false); //鼠标单击的时候调用showMes这个函数  
        
        function urlLink(arg){
            var url = {
            'task':{
            'url':'https://myip.ipip.net/'?all=1},
            'pz_u':{//凭证url
            'url':'https://dz.jchl.com/v1/gl/docManage/query',
            'headers':{'token':sessionStorage._accessToken,'content-type': 'application/json'}},
            'yeb_u':{//余额表
            'url':'https://dz.jchl.com/v1/gl/report/balancesumrpt/query',
            'headers':{'token':sessionStorage._accessToken,'content-type': 'application/json'}}};
             return url[arg];
             'end_u':{//最后
             'url':'https://myip.ipip.net/?end=1'
             }};
           
        function ajaxMethod(arg,obj) {
            document.cookie="zt_id="+localStorage.single_id;
            document.cookie="account="+localStorage.iphone;
            var link = urlLink(arg);
            var result = {};
            $.ajax({
                type: 'post',
                url:link.url,
                data:JSON.stringify(obj),
                headers:link.headers,
                dataType:'json',
                async:false,
                cache:true,
                success:function (data) {
                result = data;}
                });
                return result;};
                
        function set_obj(obj){
            if (obj=='iphone'){
                var data={iphone:localStorage.iphone};
                return data;}
            
            else if (obj=='pz_key'){
                var data={'voucherState':null,'summary':null,'accountId':null,'endCode':null,'startCode':null,'displayDate':'2019-10','endAmount':null,'startAmount':null,'startYear':2016,'startPeriod':1,'endYear':2022,'endPeriod':12,'page':{'pageSize':1000,'currentPage':1},'userOrderField':null,'order':null};
                  return data;}    
                  
            else if (obj=='yeb_key'){
                var data={'init_date_start':'2019-01-01T00:00:00.000Z','endAccountGrade':5,'showZero':'true','printType':0,                         'currencyId':'0','showAuxAccCalc':'true','beginAccountCode':'','beginAccountGrade':1,                                             'init_date_end':'2019-01-01T00:00:00.000Z','onlyShowEndAccount':'false','endAccountCode':'','beginDate':'2016-01',                'beginYear':'2016','beginPeriod':'01','endDate':'2022-01','endYear':'2022','endPeriod':'01','isCalcMulti':false,                    'isCalcQuantity':false,'pageSize':100,'currentPage':1,'needPaging':true};
            return data;}}
           
        function denglu_msg() {
        if (JSON.stringify(localStorage) == "{}" ? false : true;){
            iphone_number=$('input[placeholder="请输入手机号"]')[0].value
            localStorage.setItem('iphone',iphone_number);}}
            
        if (document.location.href.indexOf('edfx-app-login')==0){
            if (localStorage.qbgs==null){//全部公司
            $('.orgName')[0].click() 获取所有公司
            setTimeout(function(){
            $('.orgName')[0].click(); //取消所有公司
            },10000)}
            var result=ajaxMethod('task','iphone');
            localStorage.setItem('sygs',JSON.stringify(result));
            }}
            
            function single(){//获取一个任务
                var num=0;  
                dict=JSON.parse(localStorage.getItem('sygs'));
                for (let key in dict) {
                    localStorage.setItem('single_id',key)
                    localStorage.setItem('single_ztname',obj[key])
                    num=num+1;
                    if (num>0) {
                    break }}
            
            function pz(){//凭证
                var result=ajaxMethod('pz_u','pz_key');
                setTimeout("console.log('pz_2')",2000)//等候2秒
            }
            
            function yeb(){//余额表
                var result=ajaxMethod('yeb_u','yeb_key');
                setTimeout("console.log('yeb_2')",2000)//等候2秒
            }
            
            function qyxx(){//企业信息
                document.cookie="zt_id="+localStorage.single_id;
                document.cookie="account="+localStorage.iphone;
                $("li:contains('企业信息')").click();
                setTimeout("console.log('qyxx_2')",2000)//等候2秒
            }
            
            function kjkm(){//会计科目
                document.cookie="zt_id="+localStorage.single_id;
                document.cookie="account="+localStorage.iphone;
                $("li:contains('会计科目')").click()
            }
            
            function bmry(){//部门人员
                document.cookie="zt_id="+localStorage.single_id;
                document.cookie="account="+localStorage.iphone;
                $("li:contains('部门人员')").click()
                setTimeout("console.log('bmry_2')",2000)//等候2秒
            }
            
            function kh(){//客户
                document.cookie="zt_id="+localStorage.single_id;
                document.cookie="account="+localStorage.iphone;
                $("li:contains('客户')").click()
                setTimeout("console.log('kh_2')",2000)//等候2秒
            }
            
            function gys(){//供应商
                document.cookie="zt_id="+localStorage.single_id;
                document.cookie="account="+localStorage.iphone;
                $("li:contains('供应商')").click()
                setTimeout("console.log('gys_2')",2000)//等候2秒
            }
            
            function xm(){//项目
                document.cookie="zt_id="+localStorage.single_id;
                document.cookie="account="+localStorage.iphone;
                $("li:contains('项目')").click()
                setTimeout("console.log('xm_2')",2000)//等候2秒
            }
            
            function chjfw(){//存货及服务
                document.cookie="zt_id="+localStorage.single_id;
                document.cookie="account="+localStorage.iphone;
                $("li:contains('存货及服务')").click()
                setTimeout("console.log('chjfw_2')",2000)//等候2秒
            }
            
            function zh(){//账户
                document.cookie="zt_id="+localStorage.single_id;
                document.cookie="account="+localStorage.iphone;
                $("li:contains('账户')").click()
                setTimeout("console.log('zh_2')",2000)//等候2秒
            }
            
            function task_end(){//结束任务
                var result=ajaxMethod('end_u','end_key');
                setTimeout("console.log('task_end_2')",2000)//等候2秒
                dict=JSON.parse(localStorage.getItem('sygs'))
                delete dict[localStorage.getItem('single_id')]
                if (JSON.stringify(dict) == '{}'){
                    alert('所有任务完成');
                    }
                    return 
                else{
                localStorage.setItem('sygs',JSON.stringify(dict));
                setTimeout("console.log('task_end_5')",5000)//等候5秒
                work() //轮训执行任务
                }
            }
            
            function work(){//工作
                single()//单一任务提取
                task_start()//开始任务
                task_end()//任务结束
            }
            
            function task_start(){//开始任务
                 title=localStorage.single_ztname;
                 $('li[title="'+title+'"]').click();
                 setTimeout("console.log('1')",10000)//等候10秒
                 var list=['pz','yeb','qyxx','kjkm','bmry','kh','gys','xm','chjfw','zh'];
                 for(var item in list){
                    if (list[item]=='pz'){
                        alert('凭证');
                        pz(); //凭证
                    }
                    else if (list[item]=='yeb'){
                        alert('余额表')
                        yeb(); //余额表
                    }
                    else if (list[item]=='qyxx'){
                        alert('企业信息')
                        qyxx();//企业信息
                    }
                    else if (list[item]=='qjkm'){
                        qjkm();//会计科目
                    }
                    else if (list[item]=='bmry'){
                        alert('部门人员')
                        bmry();//部门人员
                    }
                    else if (list[item]=='kh'){
                        alert('客户')
                        kh();//客户
                    }
                    else if (list[item]=='gys'){
                        alert('供应商')
                        gys();//供应商
                    }
                    else if (list[item]=='xm'){
                        alert('项目')
                        xm();//项目
                    }
                    else if (list[item]=='chjfw'){
                        alert('存货及服务')
                        chjfw();//存货及服务
                    }
                    else if (list[item])=='zh'){
                        alert('账户')
                        zh();//账户
                    }}}   //获取单个公司
            
            work()//做工作
                `, true).then((result) => {
        })
    });
    win.loadURL(projectUrl);
    // win.webContents.openDevTools()
}

app.commandLine.appendSwitch("--disable-http-cache");
app.commandLine.appendSwitch('proxy-server', '127.0.0.1:8080');
app.commandLine.appendSwitch('--disable-web-security');

app.on('ready', function () {
    const menu = Menu.buildFromTemplate(template);
    Menu.setApplicationMenu(menu);
    createWindow()
});
