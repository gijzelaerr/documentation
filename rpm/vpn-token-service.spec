%global composer_vendor         eduvpn
%global composer_project        vpn-token-service
%global composer_namespace      SURFnet/VPN/Token

%global github_owner            eduvpn
%global github_name             vpn-token-service
%global github_commit           a60776cd4678a79c88d395b8b6cca1ea42f8d600
%global github_short            %(c=%{github_commit}; echo ${c:0:7})

Name:       vpn-token-service
Version:    1.0.0
Release:    0.21%{?dist}
Summary:    VPN Token Service

Group:      Applications/Internet
License:    AGPLv3+

URL:        https://github.com/%{github_owner}/%{github_name}
Source0:    %{url}/archive/%{github_commit}/%{name}-%{version}-%{github_short}.tar.gz
Source1:    %{name}-httpd.conf

BuildArch:  noarch
BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n) 

BuildRequires:  %{_bindir}/phpunit
BuildRequires:  php(language) >= 5.4.0
BuildRequires:  php-date
BuildRequires:  php-json
BuildRequires:  php-libsodium
BuildRequires:  php-pdo
BuildRequires:  php-composer(twig/twig) < 2
BuildRequires:  php-composer(fkooman/oauth2-server)
BuildRequires:  php-composer(paragonie/constant_time_encoding)
BuildRequires:  php-composer(fedora/autoloader)

Requires:   php(language) >= 5.4.0
# the scripts in bin/ require the PHP CLI
Requires:   php-cli
Requires:   php-date
Requires:   php-json
Requires:   php-libsodium
Requires:   php-pdo
Requires:   php-composer(twig/twig) < 2
Requires:   php-composer(fkooman/oauth2-server)
Requires:   php-composer(paragonie/constant_time_encoding)
Requires:   php-composer(fedora/autoloader)
%if 0%{?fedora} >= 24
Requires:   httpd-filesystem
%else
# EL7 does not have httpd-filesystem
Requires:   httpd
%endif

Requires(post): /usr/sbin/semanage
Requires(postun): /usr/sbin/semanage

%description
VPN Admin Portal.

%prep
%setup -qn %{github_name}-%{github_commit} 

sed -i "s|require_once sprintf('%s/vendor/autoload.php', dirname(__DIR__));|require_once '%{_datadir}/%{name}/src/%{composer_namespace}/autoload.php';|" bin/*
sed -i "s|require_once sprintf('%s/vendor/autoload.php', dirname(__DIR__));|require_once '%{_datadir}/%{name}/src/%{composer_namespace}/autoload.php';|" web/*.php
sed -i "s|dirname(__DIR__)|'%{_datadir}/%{name}'|" bin/*

%build
cat <<'AUTOLOAD' | tee src/autoload.php
<?php
require_once '%{_datadir}/php/Fedora/Autoloader/autoload.php';

\Fedora\Autoloader\Autoload::addPsr4('SURFnet\\VPN\\Token\\', __DIR__);
\Fedora\Autoloader\Dependencies::required(array(
    '%{_datadir}/php/fkooman/OAuth/Server/autoload.php',
    '%{_datadir}/php/Twig/autoload.php',
    '%{_datadir}/php/ParagonIE/ConstantTime/autoload.php',
));
AUTOLOAD

%install
install -m 0644 -D -p %{SOURCE1} %{buildroot}%{_sysconfdir}/httpd/conf.d/%{name}.conf

mkdir -p %{buildroot}%{_datadir}/%{name}
cp -pr web views %{buildroot}%{_datadir}/%{name}
mkdir -p %{buildroot}%{_datadir}/%{name}/src/%{composer_namespace}
cp -pr src/* %{buildroot}%{_datadir}/%{name}/src/%{composer_namespace}
mkdir -p %{buildroot}%{_bindir}
(
cd bin
for phpFileName in $(ls *)
do
    binFileName=$(basename ${phpFileName} .php)
    cp -pr ${phpFileName} %{buildroot}%{_bindir}/%{name}-${binFileName}
    chmod 0755 %{buildroot}%{_bindir}/%{name}-${binFileName}
done
)

mkdir -p %{buildroot}%{_sysconfdir}/%{name}
cp -pr config/config.php.example %{buildroot}%{_sysconfdir}/%{name}/config.php
ln -s ../../../etc/%{name} %{buildroot}%{_datadir}/%{name}/config

mkdir -p %{buildroot}%{_localstatedir}/lib/%{name}
ln -s ../../../var/lib/%{name} %{buildroot}%{_datadir}/%{name}/data

%check
phpunit --bootstrap=%{buildroot}/%{_datadir}/%{name}/src/%{composer_namespace}/autoload.php

%post
semanage fcontext -a -t httpd_sys_rw_content_t '%{_localstatedir}/lib/%{name}(/.*)?' 2>/dev/null || :
restorecon -R %{_localstatedir}/lib/%{name} || :
# remove template cache if it is there
rm -rf %{_localstatedir}/lib/%{name}/tpl/* >/dev/null 2>/dev/null || :

%postun
if [ $1 -eq 0 ] ; then  # final removal
semanage fcontext -d -t httpd_sys_rw_content_t '%{_localstatedir}/lib/%{name}(/.*)?' 2>/dev/null || :
fi

%files
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/httpd/conf.d/%{name}.conf
%dir %attr(0750,root,apache) %{_sysconfdir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/config.php
%{_bindir}/*
%{_datadir}/%{name}/src
%{_datadir}/%{name}/web
%{_datadir}/%{name}/data
%{_datadir}/%{name}/views
%{_datadir}/%{name}/config
%dir %attr(0700,apache,apache) %{_localstatedir}/lib/%{name}
%doc README.md CHANGES.md composer.json config/config.php.example
%license LICENSE

%changelog
* Wed Mar 08 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.21
- rebuilt

* Thu Feb 16 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.20
- rebuilt

* Wed Feb 15 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.19
- rebuilt

* Thu Feb 02 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.18
- rebuilt

* Wed Feb 01 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.17
- rebuilt

* Wed Feb 01 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.16
- rebuilt

* Wed Feb 01 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.15
- rebuilt

* Wed Feb 01 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.14
- rebuilt

* Wed Feb 01 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.13
- rebuilt

* Wed Feb 01 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.12
- rebuilt

* Sun Jan 29 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.11
- rebuilt

* Fri Jan 27 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.10
- rebuilt

* Fri Jan 27 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.9
- rebuilt

* Fri Jan 27 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.8
- rebuilt

* Thu Jan 26 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.7
- rebuilt

* Thu Jan 26 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.6
- rebuilt

* Thu Jan 26 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.5
- rebuilt

* Wed Jan 25 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.4
- rebuilt

* Wed Jan 25 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.3
- rebuilt

* Wed Jan 25 2017 François Kooman <fkooman@tuxed.net> - 1.0.0-0.2
- initial package
