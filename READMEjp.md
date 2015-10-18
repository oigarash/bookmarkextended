Bookmark Extended

Sublime Bookmark Extendedは、Sublime 2, 3のプラグインで、Sublime Text Editorのデフォルト機能であるBookmark機能を拡張しています。

# Install
Package Controlからのインストールをおすすめします。

# Usage
Bookmark Extendedでは、以下の機能を拡張しています。

- Bookmarkへのコメントの追加
- Bookmarkの一覧の表示
- Bookmarkをバッファ上にまとめて表示

Bookmarkの追加や削除、移動はSublime Editorのデフォルトの機能と同じです。


デフォルトに加えて、Context Menu(Bookmark Extended)も追加しています。

Bookmarkのトグル: Goto > Bookmarks > Toggle Bookmark, ⌘+F2, Quick Panel, From Context Menu
Bookmarkの全削除: Goto > Bookmarks > Clear Bookmarks, ⇧+⌘+F2, Quick Panel, From Context Menu

Bookmarkの一覧を確認したい場合は、Context Menuに表示されるので、そこから選択するか、Quick Panel上に表示することも可能です。

## Bookmarkへのコメントの追加


# Settings

enable_all_views: Bookmarkを表示する際に、現在開いている全てのViewを対象にする場合は true, アクティブのViewのみにする場合は false にしてください。

    {
        "enable_all_views": true,
    }

hightlight_bookmark: Sublime 3のみ有効です。Bookmarkした行をハイライトします。 highlight_scopeはHightlightに利用するScope(色)です。利用できるScopeはテーマによって異なります。

    {
        "highlight_bookmark": false,
        "highlight_socpe": "string",
    }
